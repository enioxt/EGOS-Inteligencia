#!/usr/bin/env python3
"""Download CEPIM (barred NGOs) data from Portal da Transparencia.

Usage:
    python etl/scripts/download_cepim.py
    python etl/scripts/download_cepim.py --date 202601
    python etl/scripts/download_cepim.py --output-dir ./data/cepim
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

# Expected columns in the government CSV.
# Accept both "MOTIVO IMPEDIMENTO" and "MOTIVO DO IMPEDIMENTO" (current format).
EXPECTED_COLUMNS = [
    "CNPJ ENTIDADE",
    "NOME ENTIDADE",
    "NÚMERO CONVÊNIO",
    "ÓRGÃO CONCEDENTE",
]

# The column name changed from "MOTIVO IMPEDIMENTO" to "MOTIVO DO IMPEDIMENTO".
# We normalize to "MOTIVO IMPEDIMENTO" for pipeline compatibility.
MOTIVO_ALIASES = ["MOTIVO DO IMPEDIMENTO", "MOTIVO IMPEDIMENTO"]


def _find_csv_in_dir(directory: Path) -> Path | None:
    """Find the first CSV file in a directory."""
    csvs = list(directory.glob("*.csv"))
    return csvs[0] if csvs else None


def _download_dataset(
    date_str: str, output_dir: Path, *, skip_existing: bool, timeout: int,
) -> Path | None:
    """Download and extract the CEPIM dataset."""
    url = f"{BASE_URL}/cepim/{date_str}"
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    zip_name = f"cepim_{date_str}.zip"
    zip_path = raw_dir / zip_name

    if skip_existing and zip_path.exists():
        logger.info("Skipping (exists): %s", zip_name)
    else:
        if not download_file(url, zip_path, timeout=timeout):
            return None

    # Extract
    extract_dir = raw_dir / "cepim_extracted"
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
    """Read raw CSV, validate columns, write pipeline-ready CSV."""
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

    logger.info("CEPIM: %d rows, columns: %s", len(df), list(df.columns))

    # Validate expected columns are present
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        logger.warning("CEPIM: missing expected columns: %s", missing)

    # Normalize "MOTIVO DO IMPEDIMENTO" -> "MOTIVO IMPEDIMENTO" for pipeline compatibility
    for alias in MOTIVO_ALIASES:
        if alias in df.columns and alias != "MOTIVO IMPEDIMENTO":
            df = df.rename(columns={alias: "MOTIVO IMPEDIMENTO"})
            logger.info("CEPIM: renamed '%s' -> 'MOTIVO IMPEDIMENTO'", alias)
            break

    df.to_csv(output_path, sep=";", index=False, encoding="latin-1")
    logger.info("Wrote %d rows to %s", len(df), output_path)
    return True


@click.command()
@click.option(
    "--date",
    default=lambda: datetime.now().strftime("%Y%m"),
    help="Date for download URL (YYYYMM). Defaults to current month.",
)
@click.option("--output-dir", default="./data/cepim", help="Output directory")
@click.option("--skip-existing/--no-skip-existing", default=True, help="Skip existing ZIPs")
@click.option("--timeout", type=int, default=300, help="Download timeout in seconds")
def main(date: str, output_dir: str, skip_existing: bool, timeout: int) -> None:
    """Download CEPIM barred NGO data."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    logger.info("=== CEPIM ===")
    csv_path = _download_dataset(date, out, skip_existing=skip_existing, timeout=timeout)
    if csv_path is None:
        logger.warning("Failed to download CEPIM")
        sys.exit(1)

    output_path = out / "cepim.csv"
    if not _process_csv(csv_path, output_path):
        sys.exit(1)

    logger.info("=== Done ===")


if __name__ == "__main__":
    main()
