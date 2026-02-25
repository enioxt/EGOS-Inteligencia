#!/usr/bin/env python3
"""Download EU consolidated sanctions list.

Downloads the CSV from the EU Financial Sanctions Files (FSD) portal.

Usage:
    python etl/scripts/download_eu_sanctions.py
    python etl/scripts/download_eu_sanctions.py --output-dir ./data/eu_sanctions
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click

# Allow imports from scripts/ directory
sys.path.insert(0, str(Path(__file__).parent))
from _download_utils import download_file

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

EU_SANCTIONS_URL = (
    "https://webgate.ec.europa.eu/fsd/fsf/public/files/"
    "csvFullSanctionsList/content?token={token}"
)


@click.command()
@click.option("--output-dir", default="./data/eu_sanctions", help="Output directory")
@click.option(
    "--skip-existing/--no-skip-existing", default=True, help="Skip existing files"
)
@click.option("--timeout", type=int, default=300, help="Download timeout in seconds")
def main(output_dir: str, skip_existing: bool, timeout: int) -> None:
    """Download EU consolidated sanctions list CSV."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    dest = out / "eu_sanctions.csv"

    if skip_existing and dest.exists():
        logger.info("Skipping (exists): %s", dest.name)
        return

    logger.info("=== Downloading EU consolidated sanctions list ===")
    if download_file(EU_SANCTIONS_URL, dest, timeout=timeout):
        logger.info("=== Done: EU sanctions downloaded to %s ===", dest)
    else:
        logger.warning("Failed to download EU sanctions list")
        sys.exit(1)


if __name__ == "__main__":
    main()
