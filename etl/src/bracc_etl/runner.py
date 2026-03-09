import logging
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import click
from neo4j import GraphDatabase

from bracc_etl.linking_hooks import run_post_load_hooks
from bracc_etl.pipelines.bcb import BcbPipeline
from bracc_etl.pipelines.bndes import BndesPipeline
from bracc_etl.pipelines.caged import CagedPipeline
from bracc_etl.pipelines.camara import CamaraPipeline
from bracc_etl.pipelines.camara_inquiries import CamaraInquiriesPipeline
from bracc_etl.pipelines.ceaf import CeafPipeline
from bracc_etl.pipelines.cepim import CepimPipeline
from bracc_etl.pipelines.cnpj import CNPJPipeline
from bracc_etl.pipelines.comprasnet import ComprasnetPipeline
from bracc_etl.pipelines.cpgf import CpgfPipeline
from bracc_etl.pipelines.cvm import CvmPipeline
from bracc_etl.pipelines.cvm_funds import CvmFundsPipeline
from bracc_etl.pipelines.datajud import DatajudPipeline
from bracc_etl.pipelines.datasus import DatasusPipeline
from bracc_etl.pipelines.dou import DouPipeline
from bracc_etl.pipelines.eu_sanctions import EuSanctionsPipeline
from bracc_etl.pipelines.holdings import HoldingsPipeline
from bracc_etl.pipelines.ibama import IbamaPipeline
from bracc_etl.pipelines.icij import ICIJPipeline
from bracc_etl.pipelines.inep import InepPipeline
from bracc_etl.pipelines.leniency import LeniencyPipeline
from bracc_etl.pipelines.mides import MidesPipeline
from bracc_etl.pipelines.ofac import OfacPipeline
from bracc_etl.pipelines.opensanctions import OpenSanctionsPipeline
from bracc_etl.pipelines.pep_cgu import PepCguPipeline
from bracc_etl.pipelines.pgfn import PgfnPipeline
from bracc_etl.pipelines.pncp import PncpPipeline
from bracc_etl.pipelines.querido_diario import QueridoDiarioPipeline
from bracc_etl.pipelines.rais import RaisPipeline
from bracc_etl.pipelines.renuncias import RenunciasPipeline
from bracc_etl.pipelines.sanctions import SanctionsPipeline
from bracc_etl.pipelines.senado import SenadoPipeline
from bracc_etl.pipelines.senado_cpis import SenadoCpisPipeline
from bracc_etl.pipelines.siconfi import SiconfiPipeline
from bracc_etl.pipelines.siop import SiopPipeline
from bracc_etl.pipelines.stf import StfPipeline
from bracc_etl.pipelines.tcu import TcuPipeline
from bracc_etl.pipelines.transferegov import TransferegovPipeline
from bracc_etl.pipelines.transparencia import TransparenciaPipeline
from bracc_etl.pipelines.tse import TSEPipeline
from bracc_etl.pipelines.tse_bens import TseBensPipeline
from bracc_etl.pipelines.tse_filiados import TseFiliadosPipeline
from bracc_etl.pipelines.un_sanctions import UnSanctionsPipeline
from bracc_etl.pipelines.viagens import ViagensPipeline
from bracc_etl.pipelines.world_bank import WorldBankPipeline

PIPELINES: dict[str, type] = {
    "cnpj": CNPJPipeline,
    "tse": TSEPipeline,
    "transparencia": TransparenciaPipeline,
    "sanctions": SanctionsPipeline,
    "pep_cgu": PepCguPipeline,
    "bndes": BndesPipeline,
    "pgfn": PgfnPipeline,
    "ibama": IbamaPipeline,
    "comprasnet": ComprasnetPipeline,
    "tcu": TcuPipeline,
    "transferegov": TransferegovPipeline,
    "rais": RaisPipeline,
    "inep": InepPipeline,
    "dou": DouPipeline,
    "datasus": DatasusPipeline,
    "icij": ICIJPipeline,
    "opensanctions": OpenSanctionsPipeline,
    "cvm": CvmPipeline,
    "cvm_funds": CvmFundsPipeline,
    "camara": CamaraPipeline,
    "camara_inquiries": CamaraInquiriesPipeline,
    "senado": SenadoPipeline,
    "ceaf": CeafPipeline,
    "cepim": CepimPipeline,
    "cpgf": CpgfPipeline,
    "leniency": LeniencyPipeline,
    "ofac": OfacPipeline,
    "holdings": HoldingsPipeline,
    "viagens": ViagensPipeline,
    "siop": SiopPipeline,
    "pncp": PncpPipeline,
    "renuncias": RenunciasPipeline,
    "siconfi": SiconfiPipeline,
    "tse_bens": TseBensPipeline,
    "tse_filiados": TseFiliadosPipeline,
    "bcb": BcbPipeline,
    "stf": StfPipeline,
    "caged": CagedPipeline,
    "eu_sanctions": EuSanctionsPipeline,
    "un_sanctions": UnSanctionsPipeline,
    "world_bank": WorldBankPipeline,
    "senado_cpis": SenadoCpisPipeline,
    "mides": MidesPipeline,
    "querido_diario": QueridoDiarioPipeline,
    "datajud": DatajudPipeline,
}


# Pipeline dependency groups for parallel execution.
# Group 0 (foundation) MUST run first — other pipelines link to Company/Person nodes.
# Groups 1+ are independent and can run in parallel.
PIPELINE_GROUPS: list[list[str]] = [
    # Group 0: Foundation data (sequential)
    ["cnpj"],
    # Group 1: Sanctions & compliance (independent, parallel)
    ["sanctions", "pep_cgu", "opensanctions", "ofac", "eu_sanctions", "un_sanctions",
     "leniency", "cepim", "world_bank"],
    # Group 2: Electoral & legislative (independent, parallel)
    ["tse", "tse_bens", "tse_filiados", "camara", "camara_inquiries",
     "senado", "senado_cpis"],
    # Group 3: Government finance & procurement (independent, parallel)
    ["transparencia", "comprasnet", "pncp", "transferegov", "cpgf",
     "viagens", "siop", "siconfi", "renuncias", "bndes", "pgfn"],
    # Group 4: Regulatory, judicial & other (independent, parallel)
    ["tcu", "stf", "datajud", "dou", "bcb", "cvm", "cvm_funds",
     "ibama", "icij", "holdings", "ceaf", "inep", "datasus",
     "rais", "caged", "mides", "querido_diario"],
]

logger = logging.getLogger(__name__)


def _run_single_pipeline(
    source: str,
    neo4j_uri: str,
    neo4j_user: str,
    neo4j_password: str,
    neo4j_database: str,
    data_dir: str,
    limit: int | None,
    chunk_size: int,
    linking_tier: str,
) -> tuple[str, bool, float, str]:
    """Run a single pipeline in a subprocess. Returns (source, success, elapsed_secs, error)."""
    os.environ["NEO4J_DATABASE"] = neo4j_database
    started = time.monotonic()
    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        pipeline_cls = PIPELINES[source]
        try:
            pipeline = pipeline_cls(
                driver=driver, data_dir=data_dir, limit=limit, chunk_size=chunk_size,
            )
        except TypeError:
            pipeline = pipeline_cls(
                driver=driver, data_dir=data_dir, limit=limit, chunk_size=chunk_size,
            )
        pipeline.run()
        run_post_load_hooks(
            driver=driver, source=source, neo4j_database=neo4j_database,
            linking_tier=linking_tier, run_id=getattr(pipeline, "run_id", None),
        )
        driver.close()
        return (source, True, time.monotonic() - started, "")
    except Exception as exc:
        return (source, False, time.monotonic() - started, str(exc)[:500])


@click.group()
def cli() -> None:
    """BRACC ETL — Data ingestion pipelines for Brazilian public data."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@cli.command()
@click.option("--source", required=True, help="Pipeline name (see 'sources' command)")
@click.option("--neo4j-uri", default="bolt://localhost:7687", help="Neo4j URI")
@click.option("--neo4j-user", default="neo4j", help="Neo4j user")
@click.option("--neo4j-password", required=True, help="Neo4j password")
@click.option("--neo4j-database", default="neo4j", help="Neo4j database")
@click.option("--data-dir", default="./data", help="Directory for downloaded data")
@click.option("--limit", type=int, default=None, help="Limit rows processed")
@click.option("--chunk-size", type=int, default=50_000, help="Chunk size for batch processing")
@click.option(
    "--linking-tier",
    type=click.Choice(["community", "full"]),
    default=os.getenv("LINKING_TIER", "full"),
    show_default=True,
    help="Post-load linking strategy tier",
)
@click.option("--streaming/--no-streaming", default=False, help="Streaming mode")
@click.option("--start-phase", type=int, default=1, help="Skip to phase N")
@click.option("--history/--no-history", default=False, help="Enable history mode when supported")
def run(
    source: str,
    neo4j_uri: str,
    neo4j_user: str,
    neo4j_password: str,
    neo4j_database: str,
    data_dir: str,
    limit: int | None,
    chunk_size: int,
    linking_tier: str,
    streaming: bool,
    start_phase: int,
    history: bool,
) -> None:
    """Run an ETL pipeline."""
    os.environ["NEO4J_DATABASE"] = neo4j_database
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    if source not in PIPELINES:
        available = ", ".join(PIPELINES.keys())
        raise click.ClickException(f"Unknown source: {source}. Available: {available}")

    pipeline_cls = PIPELINES[source]
    try:
        pipeline = pipeline_cls(
            driver=driver,
            data_dir=data_dir,
            limit=limit,
            chunk_size=chunk_size,
            history=history,
        )
    except TypeError:
        pipeline = pipeline_cls(
            driver=driver,
            data_dir=data_dir,
            limit=limit,
            chunk_size=chunk_size,
        )

    if streaming and hasattr(pipeline, "run_streaming"):
        pipeline.run_streaming(start_phase=start_phase)
    else:
        pipeline.run()

    run_post_load_hooks(
        driver=driver,
        source=source,
        neo4j_database=neo4j_database,
        linking_tier=linking_tier,
        run_id=getattr(pipeline, "run_id", None),
    )

    driver.close()


@cli.command("run-all")
@click.option("--neo4j-uri", default="bolt://localhost:7687", help="Neo4j URI")
@click.option("--neo4j-user", default="neo4j", help="Neo4j user")
@click.option("--neo4j-password", required=True, help="Neo4j password")
@click.option("--neo4j-database", default="neo4j", help="Neo4j database")
@click.option("--data-dir", default="./data", help="Directory for downloaded data")
@click.option("--limit", type=int, default=None, help="Limit rows processed")
@click.option("--chunk-size", type=int, default=50_000, help="Chunk size for batch processing")
@click.option(
    "--linking-tier",
    type=click.Choice(["community", "full"]),
    default=os.getenv("LINKING_TIER", "full"),
    show_default=True,
    help="Post-load linking strategy tier",
)
@click.option("--workers", type=int, default=4, help="Max parallel workers per group")
@click.option("--skip-cnpj", is_flag=True, help="Skip CNPJ foundation pipeline")
@click.option("--group", type=int, default=None, help="Run only a specific group (0-4)")
@click.option("--dry-run", is_flag=True, help="Show execution plan without running")
def run_all(
    neo4j_uri: str,
    neo4j_user: str,
    neo4j_password: str,
    neo4j_database: str,
    data_dir: str,
    limit: int | None,
    chunk_size: int,
    linking_tier: str,
    workers: int,
    skip_cnpj: bool,
    group: int | None,
    dry_run: bool,
) -> None:
    """Run all ETL pipelines with parallel execution by dependency group."""
    groups_to_run = PIPELINE_GROUPS if group is None else [PIPELINE_GROUPS[group]]
    if skip_cnpj and group is None:
        groups_to_run = groups_to_run[1:]

    total_pipelines = sum(len(g) for g in groups_to_run)
    click.echo(f"\n{'='*60}")
    click.echo(f"BRACC ETL — Parallel Runner")
    click.echo(f"{'='*60}")
    click.echo(f"Pipelines: {total_pipelines} | Workers: {workers} | Groups: {len(groups_to_run)}")
    click.echo(f"Neo4j: {neo4j_uri} | Database: {neo4j_database}")

    for i, grp in enumerate(groups_to_run):
        group_idx = PIPELINE_GROUPS.index(grp) if grp in PIPELINE_GROUPS else i
        parallel = len(grp) > 1
        mode = f"parallel ({min(workers, len(grp))} workers)" if parallel else "sequential"
        click.echo(f"\n  Group {group_idx}: [{mode}] {', '.join(grp)}")

    if dry_run:
        click.echo(f"\n✅ Dry run complete. {total_pipelines} pipelines would run.")
        return

    all_results: list[tuple[str, bool, float, str]] = []
    total_start = time.monotonic()

    for grp_idx, grp in enumerate(groups_to_run):
        real_idx = PIPELINE_GROUPS.index(grp) if grp in PIPELINE_GROUPS else grp_idx
        click.echo(f"\n{'─'*40}")
        click.echo(f"▶ Group {real_idx}: {len(grp)} pipeline(s)")

        if len(grp) == 1:
            result = _run_single_pipeline(
                grp[0], neo4j_uri, neo4j_user, neo4j_password,
                neo4j_database, data_dir, limit, chunk_size, linking_tier,
            )
            all_results.append(result)
            status = "✅" if result[1] else "❌"
            click.echo(f"  {status} {result[0]} ({result[2]:.1f}s)")
            if not result[1]:
                click.echo(f"     Error: {result[3][:200]}")
        else:
            w = min(workers, len(grp))
            with ProcessPoolExecutor(max_workers=w) as executor:
                futures = {
                    executor.submit(
                        _run_single_pipeline,
                        src, neo4j_uri, neo4j_user, neo4j_password,
                        neo4j_database, data_dir, limit, chunk_size, linking_tier,
                    ): src
                    for src in grp
                }
                for future in as_completed(futures):
                    result = future.result()
                    all_results.append(result)
                    status = "✅" if result[1] else "❌"
                    click.echo(f"  {status} {result[0]} ({result[2]:.1f}s)")
                    if not result[1]:
                        click.echo(f"     Error: {result[3][:200]}")

    total_elapsed = time.monotonic() - total_start
    succeeded = sum(1 for r in all_results if r[1])
    failed = sum(1 for r in all_results if not r[1])

    click.echo(f"\n{'='*60}")
    click.echo(f"SUMMARY: {succeeded} succeeded, {failed} failed, {total_elapsed:.1f}s total")
    if failed:
        click.echo(f"\nFailed pipelines:")
        for r in all_results:
            if not r[1]:
                click.echo(f"  ❌ {r[0]}: {r[3][:200]}")
    click.echo(f"{'='*60}\n")


@cli.command()
@click.option("--output-dir", default="./data/cnpj", help="Output directory")
@click.option("--files", type=int, default=10, help="Number of files per type (0-9)")
@click.option("--skip-existing/--no-skip-existing", default=True)
def download(output_dir: str, files: int, skip_existing: bool) -> None:
    """Download CNPJ data from Receita Federal."""
    import zipfile
    from pathlib import Path

    import httpx

    logger = logging.getLogger(__name__)

    base_url = "https://dadosabertos.rfb.gov.br/CNPJ/"
    file_types = ["Empresas", "Socios", "Estabelecimentos"]

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for file_type in file_types:
        for i in range(min(files, 10)):
            filename = f"{file_type}{i}.zip"
            url = f"{base_url}{filename}"
            dest = out / filename
            try:
                if skip_existing and dest.exists():
                    logger.info("Skipping (exists): %s", dest.name)
                    continue

                logger.info("Downloading %s...", url)
                with httpx.stream("GET", url, follow_redirects=True, timeout=300) as response:
                    response.raise_for_status()
                    with open(dest, "wb") as f:
                        for chunk in response.iter_bytes(chunk_size=8192):
                            f.write(chunk)
                logger.info("Downloaded: %s", dest.name)

                logger.info("Extracting %s...", dest.name)
                with zipfile.ZipFile(dest, "r") as zf:
                    zf.extractall(out)
            except httpx.HTTPError:
                logger.warning("Failed to download %s (may not exist)", filename)


@cli.command()
def sources() -> None:
    """List available data sources."""
    click.echo("Available pipelines:")
    for name in sorted(PIPELINES):
        click.echo(f"  {name}")


if __name__ == "__main__":
    cli()
