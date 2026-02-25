#!/usr/bin/env python3
"""Download World Bank Group debarred firms and individuals list."""

from __future__ import annotations

import csv
import logging
from pathlib import Path

import click
import httpx

logger = logging.getLogger(__name__)

# World Bank JSON API for sanctioned firms (used by their debarred-firms page)
WB_JSON_API = (
    "https://apigwext.worldbank.org/dvsvc/v1.0/json/"
    "APPLICATION/ADOBE_EXPRNCE_MGR/FIRM/SANCTIONED_FIRM"
)
WB_API_KEY = os.getenv("WORLD_BANK_API_KEY", "").strip()

# Legacy CSV endpoints (deprecated, kept as fallback)
WB_LEGACY_CSV = (
    "https://finances.worldbank.org/api/views/kvbp-7zzk/rows.csv"
    "?accessType=DOWNLOAD"
)
WB_LEGACY_CATALOG = (
    "https://apigwext.worldbank.org/dvcatalog/api/file-download/dataset/"
    "0038015/dataset-resource/000381503001"
)


def _download_json_api(dest: Path, timeout: int) -> bool:
    """Download via the World Bank JSON API and convert to CSV."""
    logger.info("Downloading from JSON API: %s", WB_JSON_API)
    try:
        resp = httpx.get(
            WB_JSON_API,
            headers={"apikey": WB_API_KEY},
            follow_redirects=True,
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        records = data["response"]["ZPROCSUPP"]
        if not records:
            logger.warning("JSON API returned 0 records")
            return False

        keys = list(records[0].keys())
        with open(dest, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(records)
        logger.info(
            "Downloaded %d records via JSON API: %s (%d bytes)",
            len(records),
            dest,
            dest.stat().st_size,
        )
        return True
    except (httpx.HTTPError, KeyError) as exc:
        logger.warning("JSON API failed: %s", exc)
        return False


def _download_csv_fallback(dest: Path, timeout: int) -> bool:
    """Try legacy CSV download endpoints as fallback."""
    for url in [WB_LEGACY_CSV, WB_LEGACY_CATALOG]:
        try:
            logger.info("Trying legacy CSV: %s", url)
            with httpx.stream(
                "GET", url, follow_redirects=True, timeout=timeout
            ) as resp:
                resp.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in resp.iter_bytes(chunk_size=8192):
                        f.write(chunk)
            logger.info("Downloaded: %s (%d bytes)", dest, dest.stat().st_size)
            return True
        except httpx.HTTPError:
            logger.warning("Failed: %s", url)
    return False


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

    if _download_json_api(dest, timeout):
        return

    if _download_csv_fallback(dest, timeout):
        return

    logger.error("All download methods failed")


if __name__ == "__main__":
    main()
