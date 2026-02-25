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
)

logger = logging.getLogger(__name__)

# EU subject types we care about
EU_TYPE_PERSON = "person"
EU_TYPE_ENTERPRISE = "enterprise"
VALID_EU_TYPES = {EU_TYPE_PERSON, EU_TYPE_ENTERPRISE}

# Cypher for name-based matching to Person nodes
MATCH_PERSON_QUERY = """
UNWIND $rows AS row
MATCH (p:Person)
WHERE p.nome = row.name
MERGE (p)-[:SANCIONADA_INTERNACIONALMENTE]->(s:InternationalSanction {sanction_id: row.sanction_id})
"""

# Cypher for name-based matching to Company nodes
MATCH_COMPANY_QUERY = """
UNWIND $rows AS row
MATCH (c:Company)
WHERE c.razao_social = row.name
MERGE (c)-[:SANCIONADA_INTERNACIONALMENTE]->(s:InternationalSanction {sanction_id: row.sanction_id})
"""


def _generate_sanction_id(name: str, program: str, regulation: str) -> str:
    """Generate a deterministic 16-char hex ID from entity name, program, and regulation."""
    raw = f"{name}|{program}|{regulation}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _clean_entity_type(raw: str) -> str:
    """Normalize EU Entity_SubjectType field."""
    return raw.strip().lower()


class EuSanctionsPipeline(Pipeline):
    """ETL pipeline for EU consolidated sanctions list.

    Loads sanctioned entities as InternationalSanction nodes and creates
    SANCIONADA_INTERNACIONALMENTE relationships via name matching to
    existing Person/Company nodes.
    """

    name = "eu_sanctions"
    source_id = "eu_sanctions"

    def __init__(
        self,
        driver: Driver,
        data_dir: str = "./data",
        limit: int | None = None,
        chunk_size: int = 50_000,
    ) -> None:
        super().__init__(driver, data_dir, limit=limit, chunk_size=chunk_size)
        self._raw: pd.DataFrame = pd.DataFrame()
        self.sanctions: list[dict[str, Any]] = []
        self.person_rels: list[dict[str, Any]] = []
        self.company_rels: list[dict[str, Any]] = []

    def extract(self) -> None:
        eu_dir = Path(self.data_dir) / "eu_sanctions"
        csv_path = eu_dir / "eu_sanctions.csv"

        if not csv_path.exists():
            logger.warning("[eu_sanctions] eu_sanctions.csv not found at %s", csv_path)
            return

        logger.info("[eu_sanctions] Reading %s", csv_path)
        self._raw = pd.read_csv(
            csv_path,
            dtype=str,
            encoding="utf-8",
            keep_default_na=False,
            on_bad_lines="skip",
            sep=",",
        )

        if self.limit:
            self._raw = self._raw.head(self.limit)

        logger.info("[eu_sanctions] Extracted %d rows", len(self._raw))

    def transform(self) -> None:
        sanctions: list[dict[str, Any]] = []
        person_rels: list[dict[str, Any]] = []
        company_rels: list[dict[str, Any]] = []

        for _, row in self._raw.iterrows():
            name_raw = str(row.get("NameAlias_WholeName", "")).strip()
            if not name_raw:
                continue

            entity_type = _clean_entity_type(str(row.get("Entity_SubjectType", "")))
            if entity_type not in VALID_EU_TYPES:
                continue

            program = str(row.get("Regulation_Programme", "")).strip()
            regulation = str(row.get("Entity_LogicalId", "")).strip()
            listed_date = str(row.get("Regulation_PublicationDate", "")).strip()
            remark = str(row.get("Entity_Remark", "")).strip()

            sanction_id = _generate_sanction_id(name_raw, program, regulation)
            name_normalized = normalize_name(name_raw)

            record: dict[str, Any] = {
                "sanction_id": sanction_id,
                "name": name_normalized,
                "original_name": name_raw,
                "entity_type": entity_type,
                "program": program,
                "regulation": regulation,
                "listed_date": listed_date,
                "remark": remark,
                "source": "eu_sanctions",
                "source_list": "EU",
            }
            sanctions.append(record)

            # Build relationship records for name-based matching
            rel = {"sanction_id": sanction_id, "name": name_normalized}
            if entity_type == EU_TYPE_PERSON:
                person_rels.append(rel)
            elif entity_type == EU_TYPE_ENTERPRISE:
                company_rels.append(rel)

        self.sanctions = deduplicate_rows(sanctions, ["sanction_id"])
        self.person_rels = deduplicate_rows(person_rels, ["sanction_id"])
        self.company_rels = deduplicate_rows(company_rels, ["sanction_id"])

        logger.info(
            "[eu_sanctions] Transformed %d InternationalSanction nodes "
            "(%d person rels, %d company rels)",
            len(self.sanctions),
            len(self.person_rels),
            len(self.company_rels),
        )

    def load(self) -> None:
        loader = Neo4jBatchLoader(self.driver)

        if self.sanctions:
            loaded = loader.load_nodes(
                "InternationalSanction", self.sanctions, key_field="sanction_id"
            )
            logger.info("[eu_sanctions] Loaded %d InternationalSanction nodes", loaded)

        if self.person_rels:
            count = loader.run_query_with_retry(
                MATCH_PERSON_QUERY, self.person_rels
            )
            logger.info(
                "[eu_sanctions] Created %d Person SANCIONADA_INT rels", count
            )

        if self.company_rels:
            count = loader.run_query_with_retry(
                MATCH_COMPANY_QUERY, self.company_rels
            )
            logger.info(
                "[eu_sanctions] Created %d Company SANCIONADA_INT rels", count
            )
