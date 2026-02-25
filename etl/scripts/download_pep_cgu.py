#!/usr/bin/env python3
"""Download CGU PEP (Politically Exposed Persons) data from Portal da Transparencia.

Usage:
    python etl/scripts/download_pep_cgu.py
    python etl/scripts/download_pep_cgu.py --date 20260201
    python etl/scripts/download_pep_cgu.py --output-dir ./data/pep_cgu
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
# The government CSVs use underscore-delimited names with accents (e.g. Nome_PEP).
# We also keep UPPER CASE aliases for robustness.
COLUMN_MAP: dict[str, str] = {
    # Current format (underscore-delimited with accents)
    "NOME_PEP": "Nome",
    "SIGLA_FUNÇÃO": "Sigla Função",
    "SIGLA_FUNCAO": "Sigla Função",
    "DESCRIÇÃO_FUNÇÃO": "Descrição Função",
    "DESCRICAO_FUNCAO": "Descrição Função",
    "NÍVEL_FUNÇÃO": "Nível Função",
    "NIVEL_FUNCAO": "Nível Função",
    "NOME_ÓRGÃO": "Nome Órgão",
    "NOME_ORGAO": "Nome Órgão",
    "DATA_INÍCIO_EXERCÍCIO": "Data Início Exercício",
    "DATA_INICIO_EXERCICIO": "Data Início Exercício",
    "DATA_FIM_EXERCÍCIO": "Data Fim Exercício",
    "DATA_FIM_EXERCICIO": "Data Fim Exercício",
    "DATA_FIM_CARÊNCIA": "Data Fim Carência",
    "DATA_FIM_CARENCIA": "Data Fim Carência",
    # Older format (space-delimited UPPER CASE)
    "CPF": "CPF",
    "NOME": "Nome",
    "SIGLA FUNCAO": "Sigla Função",
    "SIGLA FUNÇÃO": "Sigla Função",
    "DESCRICAO FUNCAO": "Descrição Função",
    "DESCRIÇÃO FUNÇÃO": "Descrição Função",
    "NIVEL FUNCAO": "Nível Função",
    "NÍVEL FUNÇÃO": "Nível Função",
    "NOME ORGAO": "Nome Órgão",
    "NOME ÓRGÃO": "Nome Órgão",
    "DATA INICIO EXERCICIO": "Data Início Exercício",
    "DATA INÍCIO EXERCÍCIO": "Data Início Exercício",
    "DATA FIM EXERCICIO": "Data Fim Exercício",
    "DATA FIM EXERCÍCIO": "Data Fim Exercício",
    "DATA FIM CARENCIA": "Data Fim Carência",
    "DATA FIM CARÊNCIA": "Data Fim Carência",
}

# Expected pipeline columns (canonical names)
EXPECTED_COLS = {
    "CPF",
    "Nome",
    "Sigla Função",
    "Descrição Função",
    "Nível Função",
    "Nome Órgão",
    "Data Início Exercício",
    "Data Fim Exercício",
    "Data Fim Carência",
}


def _find_csv_in_dir(directory: Path) -> Path | None:
    """Find the first CSV file in a directory."""
    csvs = list(directory.glob("*.csv"))
    return csvs[0] if csvs else None


def _remap_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remap real government column names to pipeline-expected names.

    Tries exact match first, then case-insensitive (upper) match via COLUMN_MAP.
    """
    rename_map: dict[str, str] = {}
    for col in df.columns:
        col_stripped = col.strip()
        # Already canonical?
        if col_stripped in EXPECTED_COLS:
            if col_stripped != col:
                rename_map[col] = col_stripped
            continue
        # Try upper-case alias lookup
        col_upper = col_stripped.upper()
        if col_upper in COLUMN_MAP:
            rename_map[col] = COLUMN_MAP[col_upper]

    return df.rename(columns=rename_map)


def _download_pep(
    date_str: str,
    output_dir: Path,
    *,
    skip_existing: bool,
    timeout: int,
) -> Path | None:
    """Download and extract the PEP dataset."""
    url = f"{BASE_URL}/pep/{date_str}"
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    zip_name = f"pep_{date_str}.zip"
    zip_path = raw_dir / zip_name

    if skip_existing and zip_path.exists():
        logger.info("Skipping (exists): %s", zip_name)
    else:
        if not download_file(url, zip_path, timeout=timeout):
            return None

    # Extract
    extract_dir = raw_dir / "pep_extracted"
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

    logger.info("PEP: %d rows, columns: %s", len(df), list(df.columns))
    mapped = _remap_columns(df)

    missing = EXPECTED_COLS - set(mapped.columns)
    if missing:
        logger.warning("PEP: missing columns after mapping: %s", missing)
        for col in missing:
            mapped[col] = ""

    # Write with semicolon delimiter and latin-1 for consistency with source
    mapped.to_csv(output_path, index=False, sep=";", encoding="latin-1")
    logger.info("Wrote %d rows to %s", len(mapped), output_path)
    return True


@click.command()
@click.option(
    "--date",
    default=lambda: datetime.now().strftime("%Y%m%d"),
    help="Date for download URL (YYYYMMDD). Defaults to today.",
)
@click.option("--output-dir", default="./data/pep_cgu", help="Output directory")
@click.option("--skip-existing/--no-skip-existing", default=True, help="Skip existing ZIPs")
@click.option("--timeout", type=int, default=300, help="Download timeout in seconds")
def main(date: str, output_dir: str, skip_existing: bool, timeout: int) -> None:
    """Download CGU PEP (Politically Exposed Persons) data."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    logger.info("=== CGU PEP ===")
    csv_path = _download_pep(date, out, skip_existing=skip_existing, timeout=timeout)
    if csv_path is None:
        logger.warning("Failed to download PEP data")
        sys.exit(1)

    output_path = out / "pep.csv"
    if not _process_csv(csv_path, output_path):
        logger.warning("Failed to process PEP CSV")
        sys.exit(1)

    logger.info("=== Done: PEP data ready at %s ===", output_path)


if __name__ == "__main__":
    main()
