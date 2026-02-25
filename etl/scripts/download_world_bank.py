#!/usr/bin/env python3
"""Download World Bank Group debarred firms and individuals list."""

from __future__ import annotations

import logging
from pathlib import Path

import click
import httpx

logger = logging.getLogger(__name__)

# World Bank publishes a CSV of all debarred/sanctioned entities
WB_URL = (
    "https://apigwext.worldbank.org/dvcatalog/api/file-download/dataset/"
    "0038015/dataset-resource/000381503001"
)
# Alternative direct CSV URL
WB_ALT_URL = (
    "https://finances.worldbank.org/api/views/kvbp-7zzk/rows.csv"
    "?accessType=DOWNLOAD"
)


@click.command()
@click.option("--output-dir", default="./data/world_bank", help="Output directory")
@click.option("--skip-existing/--no-skip-existing", default=True)
@click.option("--timeout", type=int, default=120, help="HTTP timeout in seconds")
def main(output_dir: str, skip_existing: bool, timeout: int) -> None:
    """Download World Bank debarred firms list."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    dest = out / "debarred.csv"

    if skip_existing and dest.exists():
        logger.info("Skipping (exists): %s", dest)
        return

    for url in [WB_ALT_URL, WB_URL]:
        try:
            logger.info("Downloading from %s", url)
            with httpx.stream(
                "GET", url, follow_redirects=True, timeout=timeout
            ) as resp:
                resp.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in resp.iter_bytes(chunk_size=8192):
                        f.write(chunk)
            logger.info("Downloaded: %s (%d bytes)", dest, dest.stat().st_size)
            return
        except httpx.HTTPError:
            logger.warning("Failed to download from %s, trying next URL", url)

    logger.error("All download URLs failed")


if __name__ == "__main__":
    main()
