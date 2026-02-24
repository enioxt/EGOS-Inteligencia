#!/usr/bin/env python3
"""Download CVM PAS (Processo Administrativo Sancionador) data.

Usage:
    python etl/scripts/download_cvm.py
    python etl/scripts/download_cvm.py --output-dir ./data/cvm
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).parent))
from _download_utils import download_file, extract_zip, validate_csv

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# CVM open data portal — restructured to PROCESSO/SANCIONADOR path (ZIP)
ZIP_URL = "https://dados.cvm.gov.br/dados/PROCESSO/SANCIONADOR/DADOS/processo_sancionador.zip"


@click.command()
@click.option("--output-dir", default="./data/cvm", help="Output directory")
@click.option("--skip-existing/--no-skip-existing", default=True, help="Skip existing files")
@click.option("--timeout", type=int, default=300, help="Download timeout in seconds")
def main(output_dir: str, skip_existing: bool, timeout: int) -> None:
    """Download CVM PAS sanctions data."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    zip_dest = out / "processo_sancionador.zip"
    csv_marker = list(out.glob("*.csv"))
    if skip_existing and csv_marker:
        logger.info("Skipping (CSVs already exist): %d files", len(csv_marker))
        return

    logger.info("=== Downloading processo_sancionador.zip ===")
    if not download_file(ZIP_URL, zip_dest, timeout=timeout):
        logger.error("Failed to download processo_sancionador.zip")
        sys.exit(1)

    extracted = extract_zip(zip_dest, out)
    logger.info("Extracted %d files", len(extracted))
    for f in sorted(out.glob("*.csv")):
        validate_csv(f, encoding="latin-1", sep=";")
    logger.info("=== Done ===")


if __name__ == "__main__":
    main()
