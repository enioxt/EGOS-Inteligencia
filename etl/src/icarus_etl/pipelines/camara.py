"""ETL pipeline for Camara dos Deputados CEAP expense data.

Ingests CEAP (Cota para o Exercicio da Atividade Parlamentar) expenses.
Creates Expense nodes linked to Person (deputy) via GASTOU
and to Company (supplier) via FORNECEU.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

from icarus_etl.base import Pipeline
from icarus_etl.loader import Neo4jBatchLoader
from icarus_etl.transforms import (
    deduplicate_rows,
    format_cnpj,
    format_cpf,
    normalize_name,
    parse_date,
    strip_document,
)

if TYPE_CHECKING:
    from neo4j import Driver

logger = logging.getLogger(__name__)


def _parse_brl_value(value: str) -> float:
    """Parse Brazilian numeric format (1.234,56) to float."""
    if not value or not value.strip():
        return 0.0
    cleaned = value.strip().replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _make_expense_id(deputy_id: str, date: str, supplier_doc: str, value: str) -> str:
    """Generate a stable expense ID from key fields."""
    raw = f"camara_{deputy_id}_{date}_{supplier_doc}_{value}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class CamaraPipeline(Pipeline):
    """ETL pipeline for Camara dos Deputados CEAP expenses."""

    name = "camara"
    source_id = "camara"

    def __init__(
        self,
        driver: Driver,
        data_dir: str = "./data",
        limit: int | None = None,
        chunk_size: int = 50_000,
    ) -> None:
        super().__init__(driver, data_dir, limit=limit, chunk_size=chunk_size)
        self._raw: pd.DataFrame = pd.DataFrame()
        self.expenses: list[dict[str, Any]] = []
        self.deputies: list[dict[str, Any]] = []
        self.suppliers: list[dict[str, Any]] = []
        self.gastou_rels: list[dict[str, Any]] = []
        self.forneceu_rels: list[dict[str, Any]] = []

    def extract(self) -> None:
        camara_dir = Path(self.data_dir) / "camara"
        csv_files = sorted(camara_dir.glob("*.csv"))
        if not csv_files:
            logger.warning("No CSV files found in %s", camara_dir)
            return

        frames: list[pd.DataFrame] = []
        for f in csv_files:
            df = pd.read_csv(
                f,
                sep=";",
                dtype=str,
                encoding="utf-8-sig",
                keep_default_na=False,
            )
            frames.append(df)
            logger.info("  Loaded %d rows from %s", len(df), f.name)

        self._raw = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        logger.info("Total raw rows: %d", len(self._raw))

    def transform(self) -> None:
        if self._raw.empty:
            return

        expenses: list[dict[str, Any]] = []
        deputies_map: dict[str, dict[str, Any]] = {}
        suppliers_map: dict[str, dict[str, Any]] = {}
        gastou: list[dict[str, Any]] = []
        forneceu: list[dict[str, Any]] = []
        skipped = 0

        for _, row in self._raw.iterrows():
            deputy_name = normalize_name(str(row.get("txNomeParlamentar", "")))
            deputy_cpf_raw = str(row.get("cpf", "")).strip()
            deputy_id = str(row.get("nuDeputadoId", "")).strip()
            uf = str(row.get("sgUF", "")).strip()
            partido = str(row.get("sgPartido", "")).strip()

            supplier_doc_raw = str(row.get("txtCNPJCPF", ""))
            supplier_digits = strip_document(supplier_doc_raw)
            supplier_name = normalize_name(str(row.get("txtFornecedor", "")))

            # Must have supplier document and deputy ID
            if not supplier_digits or not deputy_id:
                skipped += 1
                continue

            # Format supplier document
            if len(supplier_digits) == 14:
                supplier_doc = format_cnpj(supplier_doc_raw)
            elif len(supplier_digits) == 11:
                supplier_doc = format_cpf(supplier_doc_raw)
            else:
                skipped += 1
                continue

            expense_type = str(row.get("txtDescricao", "")).strip()
            date = parse_date(str(row.get("datEmissao", "")))
            value = _parse_brl_value(str(row.get("vlrLiquido", "")))

            expense_id = _make_expense_id(deputy_id, date, supplier_doc, str(value))

            expenses.append({
                "expense_id": expense_id,
                "deputy_id": deputy_id,
                "type": expense_type,
                "supplier_doc": supplier_doc,
                "value": value,
                "date": date,
                "description": expense_type,
                "source": "camara",
            })

            # Track deputy
            deputy_cpf_digits = strip_document(deputy_cpf_raw)
            if len(deputy_cpf_digits) == 11:
                deputy_cpf = format_cpf(deputy_cpf_raw)
                deputies_map[deputy_cpf] = {
                    "cpf": deputy_cpf,
                    "name": deputy_name,
                    "uf": uf,
                    "partido": partido,
                }
                gastou.append({
                    "source_key": deputy_cpf,
                    "target_key": expense_id,
                })

            # Track supplier
            if len(supplier_digits) == 14:
                suppliers_map[supplier_doc] = {
                    "cnpj": supplier_doc,
                    "razao_social": supplier_name,
                }
                forneceu.append({
                    "source_key": supplier_doc,
                    "target_key": expense_id,
                })
            elif len(supplier_digits) == 11:
                # Individual supplier (CPF)
                suppliers_map[supplier_doc] = {
                    "cpf": supplier_doc,
                    "name": supplier_name,
                }
                forneceu.append({
                    "source_key": supplier_doc,
                    "target_key": expense_id,
                })

        self.expenses = deduplicate_rows(expenses, ["expense_id"])
        self.deputies = list(deputies_map.values())
        self.suppliers = list(suppliers_map.values())
        self.gastou_rels = gastou
        self.forneceu_rels = forneceu

        if self.limit:
            self.expenses = self.expenses[: self.limit]

        logger.info(
            "Transformed: %d expenses, %d deputies, %d suppliers (skipped %d)",
            len(self.expenses),
            len(self.deputies),
            len(self.suppliers),
            skipped,
        )

    def load(self) -> None:
        if not self.expenses:
            logger.warning("No expenses to load")
            return

        loader = Neo4jBatchLoader(self.driver)

        # Load Expense nodes
        expense_nodes = [
            {
                "expense_id": e["expense_id"],
                "type": e["type"],
                "value": e["value"],
                "date": e["date"],
                "description": e["description"],
                "source": e["source"],
            }
            for e in self.expenses
        ]
        count = loader.load_nodes("Expense", expense_nodes, key_field="expense_id")
        logger.info("Loaded %d Expense nodes", count)

        # Load/merge Person nodes for deputies
        if self.deputies:
            count = loader.load_nodes("Person", self.deputies, key_field="cpf")
            logger.info("Merged %d deputy Person nodes", count)

        # Load/merge Company nodes for CNPJ suppliers
        company_suppliers = [s for s in self.suppliers if "cnpj" in s]
        if company_suppliers:
            count = loader.load_nodes("Company", company_suppliers, key_field="cnpj")
            logger.info("Merged %d supplier Company nodes", count)

        # Load/merge Person nodes for CPF suppliers
        person_suppliers = [s for s in self.suppliers if "cpf" in s]
        if person_suppliers:
            count = loader.load_nodes("Person", person_suppliers, key_field="cpf")
            logger.info("Merged %d supplier Person nodes", count)

        # GASTOU: Person -> Expense
        if self.gastou_rels:
            count = loader.load_relationships(
                rel_type="GASTOU",
                rows=self.gastou_rels,
                source_label="Person",
                source_key="cpf",
                target_label="Expense",
                target_key="expense_id",
            )
            logger.info("Created %d GASTOU relationships", count)

        # FORNECEU: Company/Person -> Expense
        if self.forneceu_rels:
            query = (
                "UNWIND $rows AS row "
                "MATCH (e:Expense {expense_id: row.target_key}) "
                "OPTIONAL MATCH (c:Company {cnpj: row.source_key}) "
                "OPTIONAL MATCH (p:Person {cpf: row.source_key}) "
                "WITH e, coalesce(c, p) AS supplier "
                "WHERE supplier IS NOT NULL "
                "MERGE (supplier)-[:FORNECEU]->(e)"
            )
            count = loader.run_query(query, self.forneceu_rels)
            logger.info("Created %d FORNECEU relationships", count)
