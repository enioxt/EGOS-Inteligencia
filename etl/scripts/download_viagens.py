#!/usr/bin/env python3
"""Download Government Travel (Viagens a Servico) data from Portal da Transparencia.

Usage:
    python etl/scripts/download_viagens.py
    python etl/scripts/download_viagens.py --start-year 2020 --end-year 2025
    python etl/scripts/download_viagens.py --output-dir ./data/viagens
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

import click
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _download_utils import download_file, extract_zip, validate_csv

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://portaldatransparencia.gov.br/download-de-dados"

# Real Viagem CSV columns -> pipeline expected columns.
# These are the actual headers from Portal da Transparencia *_Viagem.csv files.
COLUMN_MAP = {
    "Identificador do processo de viagem": "id_processo",
    "Número da Proposta (PCDP)": "num_proposta",
    "Situação": "situacao",
    "Viagem Urgente": "viagem_urgente",
    "Justificativa Urgência Viagem": "justificativa_urgencia",
    "Código do órgão superior": "cod_orgao_superior",
    "Nome do órgão superior": "nome_orgao_superior",
    "Código órgão solicitante": "cod_orgao",
    "Nome órgão solicitante": "nome_orgao",
    "CPF viajante": "cpf",
    "Nome": "nome",
    "Cargo": "cargo",
    "Função": "funcao",
    "Descrição Função": "descricao_funcao",
    "Período - Data de início": "data_inicio",
    "Período - Data de fim": "data_fim",
    "Destinos": "destinos",
    "Motivo": "motivo",
    "Valor diárias": "valor_diarias",
    "Valor passagens": "valor_passagens",
    "Valor devolução": "valor_devolucao",
    "Valor outros gastos": "valor_outros",
}


def _find_viagem_csvs(directory: Path) -> list[Path]:
    """Find only *_Viagem.csv files in a directory (skip Pagamento/Trecho/Passagem)."""
    return sorted(directory.glob("*_Viagem.csv"))


def _remap_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remap government column names to pipeline-expected names.

    Tries exact match first, then case-insensitive match.
    """
    rename_map: dict[str, str] = {}
    upper_map = {k.upper(): v for k, v in COLUMN_MAP.items()}

    for col in df.columns:
        col_stripped = col.strip()
        if col_stripped in COLUMN_MAP:
            rename_map[col] = COLUMN_MAP[col_stripped]
        elif col_stripped.upper() in upper_map:
            rename_map[col] = upper_map[col_stripped.upper()]

    if rename_map:
        df = df.rename(columns=rename_map)

    found = set(rename_map.values())
    expected = set(COLUMN_MAP.values())
    missing = expected - found
    if missing:
        logger.warning("Viagens: missing columns after mapping: %s", missing)

    return df


def _download_year(
    year: int,
    raw_dir: Path,
    *,
    skip_existing: bool,
    timeout: int,
) -> list[Path]:
    """Download a single year's ZIP and return extracted CSV paths."""
    url = f"{BASE_URL}/viagens/{year}"
    zip_name = f"viagens_{year}.zip"
    zip_path = raw_dir / zip_name

    if skip_existing and zip_path.exists():
        logger.info("Skipping (exists): %s", zip_name)
    else:
        if not download_file(url, zip_path, timeout=timeout):
            return []

    extract_dir = raw_dir / f"viagens_{year}_extracted"
    extract_dir.mkdir(parents=True, exist_ok=True)
    extract_zip(zip_path, extract_dir)

    # Only pick up *_Viagem.csv — skip Pagamento, Trecho, Passagem.
    viagem_csvs = _find_viagem_csvs(extract_dir)
    if not viagem_csvs:
        logger.warning("No *_Viagem.csv found in %s", extract_dir)
    return viagem_csvs


def _process_csvs(csvs: list[Path], output_path: Path) -> bool:
    """Read raw CSVs, remap columns, concatenate, and write output."""
    frames: list[pd.DataFrame] = []

    for csv_path in csvs:
        try:
            df = pd.read_csv(
                csv_path,
                sep=";",
                encoding="latin-1",
                dtype=str,
                keep_default_na=False,
            )
        except Exception as e:
            logger.warning("Failed to read %s: %s", csv_path.name, e)
            continue

        cols_preview = list(df.columns)[:5]
        logger.info("Viagens: %d rows from %s, columns: %s", len(df), csv_path.name, cols_preview)
        df = _remap_columns(df)
        frames.append(df)

    if not frames:
        logger.warning("No valid CSV data found")
        return False

    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(output_path, index=False, sep=";", encoding="latin-1")
    logger.info("Wrote %d rows to %s", len(combined), output_path)
    return True


@click.command()
@click.option("--start-year", type=int, default=None, help="Start year (default: current year)")
@click.option("--end-year", type=int, default=None, help="End year (default: current year)")
@click.option("--output-dir", default="./data/viagens", help="Output directory")
@click.option("--skip-existing/--no-skip-existing", default=True, help="Skip existing ZIPs")
@click.option("--timeout", type=int, default=600, help="Download timeout in seconds")
def main(
    start_year: int | None,
    end_year: int | None,
    output_dir: str,
    skip_existing: bool,
    timeout: int,
) -> None:
    """Download Government Travel (Viagens a Servico) data.

    By default, downloads years 2020 to current year. Use --start-year and
    --end-year to specify a custom range.
    """
    now = datetime.now()

    sy = start_year or 2020
    ey = end_year or now.year
    years_to_download = list(range(sy, ey + 1))

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    raw_dir = out / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=== Viagens download: years %d-%d ===", sy, ey)

    all_csvs: list[Path] = []
    for year in years_to_download:
        logger.info("--- Year %d ---", year)
        csvs = _download_year(year, raw_dir, skip_existing=skip_existing, timeout=timeout)
        all_csvs.extend(csvs)

    if not all_csvs:
        logger.warning("No CSVs downloaded")
        sys.exit(1)

    # Validate first CSV
    if all_csvs:
        validate_csv(all_csvs[0], encoding="latin-1", sep=";")

    output_path = out / "viagens.csv"
    if not _process_csvs(all_csvs, output_path):
        sys.exit(1)

    logger.info("=== Done: %d CSV files processed ===", len(all_csvs))


if __name__ == "__main__":
    main()
