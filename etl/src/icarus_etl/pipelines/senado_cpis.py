from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

from icarus_etl.base import Pipeline

if TYPE_CHECKING:
    from neo4j import Driver
from icarus_etl.loader import Neo4jBatchLoader
from icarus_etl.transforms import (
    deduplicate_rows,
    normalize_name,
    parse_date,
)

logger = logging.getLogger(__name__)


def _make_cpi_id(code: str, name: str) -> str:
    """Deterministic ID from CPI code + name."""
    raw = f"{code}|{name}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class SenadoCpisPipeline(Pipeline):
    """ETL pipeline for Senate CPIs (Comissões Parlamentares de Inquérito).

    Data source: BigQuery basedosdados.br_senado_cpipedia or Senate Open Data API.
    Loads CPI nodes linked to senator Person nodes via PARTICIPOU_CPI.
    """

    name = "senado_cpis"
    source_id = "senado_cpis"

    def __init__(
        self,
        driver: Driver,
        data_dir: str = "./data",
        limit: int | None = None,
        chunk_size: int = 50_000,
    ) -> None:
        super().__init__(driver, data_dir, limit=limit, chunk_size=chunk_size)
        self._raw: pd.DataFrame = pd.DataFrame()
        self.cpis: list[dict[str, Any]] = []
        self.senator_rels: list[dict[str, Any]] = []

    def extract(self) -> None:
        cpis_dir = Path(self.data_dir) / "senado_cpis"
        csv_path = cpis_dir / "cpis.csv"

        if not csv_path.exists():
            logger.warning("[senado_cpis] cpis.csv not found at %s", csv_path)
            return

        self._raw = pd.read_csv(
            csv_path,
            dtype=str,
            keep_default_na=False,
        )

        if self.limit:
            self._raw = self._raw.head(self.limit)

        logger.info("[senado_cpis] Extracted %d rows", len(self._raw))

    def transform(self) -> None:
        cpis: list[dict[str, Any]] = []
        senator_rels: list[dict[str, Any]] = []

        for _, row in self._raw.iterrows():
            code = str(row.get("codigo_cpi", "")).strip()
            nome_cpi = str(row.get("nome_cpi", "")).strip()
            if not nome_cpi:
                continue

            cpi_id = _make_cpi_id(code, nome_cpi)
            date_start = parse_date(str(row.get("data_inicio", "")))
            date_end = parse_date(str(row.get("data_fim", "")))
            subject = str(row.get("objeto", "")).strip()

            cpis.append({
                "cpi_id": cpi_id,
                "code": code,
                "name": nome_cpi,
                "date_start": date_start,
                "date_end": date_end,
                "subject": subject,
                "source": "senado_cpis",
            })

            senator_name = str(row.get("nome_parlamentar", "")).strip()
            if senator_name:
                role = str(row.get("papel", "")).strip()
                senator_rels.append({
                    "senator_name": normalize_name(senator_name),
                    "cpi_id": cpi_id,
                    "role": role,
                })

        self.cpis = deduplicate_rows(cpis, ["cpi_id"])
        self.senator_rels = senator_rels
        logger.info(
            "[senado_cpis] Transformed %d CPIs, %d senator links",
            len(self.cpis),
            len(self.senator_rels),
        )

    def load(self) -> None:
        loader = Neo4jBatchLoader(self.driver)

        if self.cpis:
            loaded = loader.load_nodes("CPI", self.cpis, key_field="cpi_id")
            logger.info("[senado_cpis] Loaded %d CPI nodes", loaded)

        if self.senator_rels:
            query = (
                "UNWIND $rows AS row "
                "MATCH (p:Person) "
                "WHERE p.name = row.senator_name "
                "MATCH (c:CPI {cpi_id: row.cpi_id}) "
                "MERGE (p)-[r:PARTICIPOU_CPI]->(c) "
                "SET r.role = row.role"
            )
            loaded = loader.run_query_with_retry(query, self.senator_rels)
            logger.info("[senado_cpis] Loaded %d PARTICIPOU_CPI rels", loaded)
