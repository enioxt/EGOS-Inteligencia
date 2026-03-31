import logging
import os
from abc import ABC, abstractmethod
from datetime import UTC, datetime

from neo4j import Driver

# Guard Brasil — lazy import to avoid hard dependency
_guard_client = None

def _get_guard_client():
    global _guard_client
    if _guard_client is None:
        try:
            from bracc_etl.guard import GuardBrasilClient
            _guard_client = GuardBrasilClient()
        except ImportError:
            pass
    return _guard_client

logger = logging.getLogger(__name__)


class Pipeline(ABC):
    """Base class for all ETL pipelines."""

    name: str
    source_id: str

    def __init__(
        self,
        driver: Driver,
        data_dir: str = "./data",
        limit: int | None = None,
        chunk_size: int = 50_000,
        neo4j_database: str | None = None,
    ) -> None:
        self.driver = driver
        self.data_dir = data_dir
        self.limit = limit
        self.chunk_size = chunk_size
        self.neo4j_database = neo4j_database or os.getenv("NEO4J_DATABASE", "neo4j")
        source_key = getattr(self, "source_id", getattr(self, "name", "unknown_source"))
        self.run_id = f"{source_key}_{datetime.now(tz=UTC).strftime('%Y%m%d%H%M%S')}"

    @abstractmethod
    def extract(self) -> None:
        """Download raw data from source."""

    @abstractmethod
    def transform(self) -> None:
        """Normalize, deduplicate, and prepare data for loading."""

    @abstractmethod
    def load(self) -> None:
        """Load transformed data into Neo4j."""

    def run(self) -> None:
        """Execute the full ETL pipeline."""
        started_at = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        self._upsert_ingestion_run(status="running", started_at=started_at)
        try:
            logger.info("[%s] Starting extraction...", self.name)
            self.extract()
            logger.info("[%s] Starting transformation...", self.name)
            self.transform()
            logger.info("[%s] Running Guard Brasil check...", self.name)
            self._guard_check()
            logger.info("[%s] Starting load...", self.name)
            self.load()
            finished_at = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            self._upsert_ingestion_run(
                status="loaded",
                started_at=started_at,
                finished_at=finished_at,
            )
            logger.info("[%s] Pipeline complete.", self.name)
        except Exception as exc:
            finished_at = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            self._upsert_ingestion_run(
                status="quality_fail",
                started_at=started_at,
                finished_at=finished_at,
                error=str(exc)[:1000],
            )
            raise

    # ── Guard Brasil integration ───────────────────────────────────────

    # Subclasses can override these to specify which columns contain free text
    guard_text_columns: list[str] = []
    # Set to True to block load on PII detection (default: log and mask)
    guard_strict: bool = False

    def _guard_check(self) -> None:
        """Run Guard Brasil PII/ATRiAN check on transformed data.

        Subclasses that set `guard_text_columns` will get automatic PII scanning.
        Falls back gracefully if Guard Brasil is unavailable.
        """
        client = _get_guard_client()
        if client is None:
            logger.debug("[%s] Guard Brasil not available — skipping", self.name)
            return

        if not self.guard_text_columns:
            logger.debug("[%s] No guard_text_columns defined — skipping", self.name)
            return

        # Check if subclass stored transformed data as a DataFrame
        df = getattr(self, "_transformed_df", None)
        if df is None:
            logger.debug("[%s] No _transformed_df attribute — skipping guard", self.name)
            return

        try:
            from bracc_etl.guard import guard_dataframe
            cols_present = [c for c in self.guard_text_columns if c in df.columns]
            if not cols_present:
                return

            guard_dataframe(df, columns=cols_present, client=client, mask_in_place=True)
            pii_total = df.get("__guard_pii_count", [0]).sum() if "__guard_pii_count" in df.columns else 0

            if pii_total > 0:
                logger.warning(
                    "[%s] Guard Brasil found %d PII occurrence(s) in columns %s",
                    self.name, pii_total, cols_present,
                )
                if self.guard_strict:
                    raise RuntimeError(
                        f"Guard Brasil blocked load: {pii_total} PII finding(s) "
                        f"in columns {cols_present}. Set guard_strict=False to mask instead."
                    )
            else:
                logger.info("[%s] Guard Brasil: clean — 0 PII findings", self.name)
        except ImportError:
            logger.debug("[%s] bracc_etl.guard not importable — skipping", self.name)
        except RuntimeError:
            raise
        except Exception as exc:
            logger.warning("[%s] Guard check failed (non-fatal): %s", self.name, exc)

    def _upsert_ingestion_run(
        self,
        *,
        status: str,
        started_at: str | None = None,
        finished_at: str | None = None,
        error: str | None = None,
    ) -> None:
        """Persist ingestion run state for operational traceability."""
        source_id = getattr(self, "source_id", getattr(self, "name", "unknown_source"))
        query = (
            "MERGE (r:IngestionRun {run_id: $run_id}) "
            "SET r.source_id = $source_id, "
            "    r.status = $status, "
            "    r.started_at = coalesce($started_at, r.started_at), "
            "    r.finished_at = coalesce($finished_at, r.finished_at), "
            "    r.error = coalesce($error, r.error), "
            "    r.rows_in = coalesce(r.rows_in, 0), "
            "    r.rows_loaded = coalesce(r.rows_loaded, 0)"
        )
        run_id = getattr(self, "run_id", f"{source_id}_manual")
        params = {
            "run_id": run_id,
            "source_id": source_id,
            "status": status,
            "started_at": started_at,
            "finished_at": finished_at,
            "error": error,
        }
        try:
            with self.driver.session(database=self.neo4j_database) as session:
                session.run(query, params)
        except Exception as exc:  # noqa: BLE001
            logger.warning("[%s] failed to persist IngestionRun: %s", self.name, exc)
