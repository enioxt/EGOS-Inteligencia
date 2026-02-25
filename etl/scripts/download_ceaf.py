#!/usr/bin/env python3
"""Download CEAF (expelled servants) data from Portal da Transparencia.

Usage:
    python etl/scripts/download_ceaf.py
    python etl/scripts/download_ceaf.py --date 20260101
    python etl/scripts/download_ceaf.py --output-dir ./data/ceaf
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

import click
import pandas as pd

# Allow imports from scripts/ directory
sys.path.insert(0, str(Path(__file__).parent))
from _download_utils import download_file, extract_zip, validate_csv

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://portaldatransparencia.gov.br/download-de-dados"

# Real government CSV columns -> pipeline expected columns.
# The government changed column names; support both old and new formats.
COLUMN_MAP = {
    # Current format (as of 2026)
    "CPF OU CNPJ DO SANCIONADO": "cpf",
    "NOME DO SANCIONADO": "nome",
    "CARGO EFETIVO": "cargo_efetivo",
    "CATEGORIA DA SANÇÃO": "tipo_punicao",
    "DATA PUBLICAÇÃO": "data_publicacao",
    "NÚMERO DO DOCUMENTO": "portaria",
    "UF ÓRGÃO SANCIONADOR": "uf",
    # Older format (kept for backward compatibility)
    "CPF SERVIDOR": "cpf",
    "NOME SERVIDOR": "nome",
    "TIPO DE PUNIÇÃO": "tipo_punicao",
    "DATA DA PUBLICAÇÃO": "data_publicacao",
    "PORTARIA DE PUNIÇÃO": "portaria",
    "UF LOTAÇÃO": "uf",
}


def _find_csv_in_dir(directory: Path) -> Path | None:
    """Find the first CSV file in a directory."""
    csvs = list(directory.glob("*.csv"))
    return csvs[0] if csvs else None


def _remap_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remap real government column names to pipeline-expected names."""
    mapped = pd.DataFrame()

    for real_col, pipeline_col in COLUMN_MAP.items():
        if real_col in df.columns:
            mapped[pipeline_col] = df[real_col]

    missing_cols = set(COLUMN_MAP.values()) - set(mapped.columns)
    if missing_cols:
        logger.warning("CEAF: missing columns after mapping: %s", missing_cols)
        for col in missing_cols:
            mapped[col] = ""

    return mapped


def _download_dataset(
    date_str: str, output_dir: Path, *, skip_existing: bool, timeout: int,
) -> Path | None:
    """Download and extract the CEAF dataset."""
    url = f"{BASE_URL}/ceaf/{date_str}"
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    zip_name = f"ceaf_{date_str}.zip"
    zip_path = raw_dir / zip_name

    if skip_existing and zip_path.exists():
        logger.info("Skipping (exists): %s", zip_name)
    else:
        if not download_file(url, zip_path, timeout=timeout):
            return None

    # Extract
    extract_dir = raw_dir / "ceaf_extracted"
    extract_dir.mkdir(parents=True, exist_ok=True)
    extracted = extract_zip(zip_path, extract_dir)
    if not extracted:
        return None

    csv_path = _find_csv_in_dir(extract_dir)
    if csv_path is None:
        logger.warning("No CSV found after extracting %s", zip_name)
        return None

    validate_csv(csv_path, encoding="latin-1", sep=";")
    return csv_path


def _process_csv(csv_path: Path, output_path: Path) -> bool:
    """Read raw CSV, remap columns, write pipeline-ready CSV."""
    try:
        df = pd.read_csv(
            csv_path,
            sep=";",
            encoding="latin-1",
            dtype=str,
            keep_default_na=False,
        )
    except Exception as e:
        logger.warning("Failed to read %s: %s", csv_path, e)
        return False

    logger.info("CEAF: %d rows, columns: %s", len(df), list(df.columns))
    mapped = _remap_columns(df)
    mapped.to_csv(output_path, index=False, encoding="latin-1")
    logger.info("Wrote %d rows to %s", len(mapped), output_path)
    return True


@click.command()
@click.option(
    "--date",
    default=lambda: datetime.now().strftime("%Y%m%d"),
    help="Date for download URL (YYYYMMDD). Defaults to today.",
)
@click.option("--output-dir", default="./data/ceaf", help="Output directory")
@click.option("--skip-existing/--no-skip-existing", default=True, help="Skip existing ZIPs")
@click.option("--timeout", type=int, default=300, help="Download timeout in seconds")
def main(date: str, output_dir: str, skip_existing: bool, timeout: int) -> None:
    """Download CEAF expelled servants data."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    logger.info("=== CEAF ===")
    csv_path = _download_dataset(date, out, skip_existing=skip_existing, timeout=timeout)
    if csv_path is None:
        logger.warning("Failed to download CEAF")
        sys.exit(1)

    output_path = out / "ceaf.csv"
    if not _process_csv(csv_path, output_path):
        sys.exit(1)

    logger.info("=== Done ===")


if __name__ == "__main__":
    main()
