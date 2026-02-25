#!/usr/bin/env python3
"""Download CAGED labor movement data from Base dos Dados (BigQuery).

Streams microdados_movimentacao from BigQuery to a local CSV.
Requires `google-cloud-bigquery` and an authenticated GCP project.

Usage:
    python etl/scripts/download_caged.py --billing-project icarus-corruptos
    python etl/scripts/download_caged.py --billing-project icarus-corruptos --start-year 2024
    python etl/scripts/download_caged.py --billing-project icarus-corruptos --skip-existing
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BQ_TABLE = "basedosdados.br_me_caged.microdados_movimentacao"

COLUMNS = [
    "cnpj_raiz",
    "sigla_uf",
    "id_municipio",
    "cnae_2_secao",
    "cnae_2_subclasse",
    "cbo_2002",
    "categoria",
    "grau_instrucao",
    "idade",
    "horas_contratuais",
    "raca_cor",
    "sexo",
    "tipo_empregador",
    "tipo_estabelecimento",
    "tipo_movimentacao",
    "tipo_deficiencia",
    "indicador_trabalho_intermitente",
    "indicador_trabalho_parcial",
    "salario_mensal",
    "saldo_movimentacao",
    "ano",
    "mes",
]

PAGE_SIZE = 100_000


def _download_caged(
    billing_project: str,
    output_dir: Path,
    start_year: int,
    *,
    skip_existing: bool = False,
) -> None:
    """Query CAGED data from BigQuery and stream to CSV."""
    from google.cloud import bigquery

    dest = output_dir / "caged.csv"
    if skip_existing and dest.exists():
        logger.info("Skipping (exists): %s", dest.name)
        return

    client = bigquery.Client(project=billing_project)

    cols = ", ".join(COLUMNS)
    sql = f"SELECT {cols} FROM `{BQ_TABLE}` WHERE ano >= {start_year}"  # noqa: S608

    logger.info("Running query: %s", sql)
    query_job = client.query(sql)

    rows_written = 0
    for i, chunk_df in enumerate(query_job.result().to_dataframe_iterable()):
        chunk_df.to_csv(dest, mode="a", header=(i == 0), index=False)
        rows_written += len(chunk_df)
        if i == 0 or rows_written % (PAGE_SIZE * 5) == 0:
            logger.info("  caged: %d rows written", rows_written)

    logger.info("Done: %s (%d rows)", dest.name, rows_written)


@click.command()
@click.option("--billing-project", required=True, help="GCP project for BigQuery billing")
@click.option("--output-dir", default="./data/caged", help="Output directory for CSV")
@click.option("--start-year", type=int, default=2023, help="Start year filter (default: 2023)")
@click.option("--skip-existing", is_flag=True, help="Skip if caged.csv already exists")
def main(
    billing_project: str,
    output_dir: str,
    start_year: int,
    skip_existing: bool,
) -> None:
    """Download CAGED labor movement data from Base dos Dados (BigQuery)."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Downloading CAGED from %s (year >= %d, billing: %s)",
        BQ_TABLE, start_year, billing_project,
    )

    _download_caged(billing_project, out, start_year, skip_existing=skip_existing)

    # Print summary
    logger.info("=== Download complete ===")
    for f in sorted(out.iterdir()):
        if f.is_file():
            size_mb = f.stat().st_size / 1e6
            logger.info("  %s: %.1f MB", f.name, size_mb)


if __name__ == "__main__":
    main()
    sys.exit(0)
