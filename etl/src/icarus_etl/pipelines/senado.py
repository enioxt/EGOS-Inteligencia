"""ETL pipeline for Senado Federal CEAPS expense data.

Ingests CEAPS (Cota para o Exercicio da Atividade Parlamentar dos Senadores)
expenses. Creates Expense nodes linked to Person (senator) via GASTOU
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


def _make_expense_id(senator_name: str, date: str, supplier_doc: str, value: str) -> str:
    """Generate a stable expense ID from key fields."""
    raw = f"senado_{senator_name}_{date}_{supplier_doc}_{value}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class SenadoPipeline(Pipeline):
    """ETL pipeline for Senado Federal CEAPS expenses."""

    name = "senado"
    source_id = "senado"

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
        self.suppliers: list[dict[str, Any]] = []
        self.forneceu_rels: list[dict[str, Any]] = []

    def extract(self) -> None:
        senado_dir = Path(self.data_dir) / "senado"
        csv_files = sorted(senado_dir.glob("*.csv"))
        if not csv_files:
            logger.warning("No CSV files found in %s", senado_dir)
            return

        frames: list[pd.DataFrame] = []
        for f in csv_files:
            df = pd.read_csv(
                f,
                sep=";",
                dtype=str,
                encoding="latin-1",
                keep_default_na=False,
                skiprows=1,
            )
            frames.append(df)
            logger.info("  Loaded %d rows from %s", len(df), f.name)

        self._raw = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        logger.info("Total raw rows: %d", len(self._raw))

    def transform(self) -> None:
        if self._raw.empty:
            return

        expenses: list[dict[str, Any]] = []
        suppliers_map: dict[str, dict[str, Any]] = {}
        forneceu: list[dict[str, Any]] = []
        skipped = 0

        for _, row in self._raw.iterrows():
            senator_name = normalize_name(str(row.get("SENADOR", "")))
            expense_type = str(row.get("TIPO_DESPESA", "")).strip()

            supplier_doc_raw = str(row.get("CNPJ_CPF", ""))
            supplier_digits = strip_document(supplier_doc_raw)
            supplier_name = normalize_name(str(row.get("FORNECEDOR", "")))

            if not supplier_digits:
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

            date = parse_date(str(row.get("DATA", "")))
            value = _parse_brl_value(str(row.get("VALOR_REEMBOLSADO", "")))
            documento = str(row.get("DOCUMENTO", "")).strip()
            detalhamento = str(row.get("DETALHAMENTO", "")).strip()

            expense_id = _make_expense_id(senator_name, date, supplier_doc, str(value))

            expenses.append({
                "expense_id": expense_id,
                "senator_name": senator_name,
                "type": expense_type,
                "supplier_doc": supplier_doc,
                "value": value,
                "date": date,
                "description": detalhamento or expense_type,
                "documento": documento,
                "source": "senado",
            })

            # Track supplier
            if len(supplier_digits) == 14:
                suppliers_map[supplier_doc] = {
                    "cnpj": supplier_doc,
                    "razao_social": supplier_name,
                }
            elif len(supplier_digits) == 11:
                suppliers_map[supplier_doc] = {
                    "cpf": supplier_doc,
                    "name": supplier_name,
                }

            forneceu.append({
                "source_key": supplier_doc,
                "target_key": expense_id,
            })

        self.expenses = deduplicate_rows(expenses, ["expense_id"])
        self.suppliers = list(suppliers_map.values())
        self.forneceu_rels = forneceu

        if self.limit:
            self.expenses = self.expenses[: self.limit]

        logger.info(
            "Transformed: %d expenses, %d suppliers (skipped %d)",
            len(self.expenses),
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
