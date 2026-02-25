#!/usr/bin/env python3
"""Download Senado CPIs data from BigQuery (basedosdados)."""

from __future__ import annotations

import csv
import logging
from pathlib import Path

import click

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--billing-project",
    default="icarus-corruptos",
    help="GCP billing project",
)
@click.option("--output-dir", default="./data/senado_cpis", help="Output directory")
@click.option("--skip-existing/--no-skip-existing", default=True)
def main(billing_project: str, output_dir: str, skip_existing: bool) -> None:
    """Download Senado CPIs from BigQuery."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    dest = out / "cpis.csv"

    if skip_existing and dest.exists():
        logger.info("Skipping (exists): %s", dest)
        return

    try:
        import google.auth
        from google.cloud import bigquery
    except ImportError:
        logger.error("Install google-cloud-bigquery: pip install google-cloud-bigquery")
        return

    credentials, _ = google.auth.default()
    client = bigquery.Client(project=billing_project, credentials=credentials)

    query = """
    SELECT *
    FROM `basedosdados.br_senado_cpipedia.microdados`
    """

    logger.info("Querying BigQuery: %s", billing_project)
    result = client.query(query).result()

    rows_written = 0
    with open(dest, "w", newline="", encoding="utf-8") as f:
        writer: csv.DictWriter | None = None
        for row in result:
            row_dict = dict(row)
            if writer is None:
                writer = csv.DictWriter(f, fieldnames=list(row_dict.keys()))
                writer.writeheader()
            writer.writerow(row_dict)
            rows_written += 1

    logger.info("Wrote %d rows to %s", rows_written, dest)


if __name__ == "__main__":
    main()
