import time
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from neo4j import AsyncSession

from icarus.dependencies import get_session
from icarus.services.neo4j_service import execute_query_single

router = APIRouter(prefix="/api/v1/meta", tags=["meta"])

_stats_cache: dict[str, Any] | None = None
_stats_cache_time: float = 0.0


@router.get("/health")
async def neo4j_health(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, str]:
    record = await execute_query_single(session, "health_check", {})
    if record and record["ok"] == 1:
        return {"neo4j": "connected"}
    return {"neo4j": "error"}


@router.get("/stats")
async def database_stats(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, Any]:
    global _stats_cache, _stats_cache_time  # noqa: PLW0603

    if _stats_cache is not None and (time.monotonic() - _stats_cache_time) < 300:
        return _stats_cache

    record = await execute_query_single(session, "meta_stats", {})
    result = {
        "total_nodes": record["total_nodes"] if record else 0,
        "total_relationships": record["total_relationships"] if record else 0,
        "person_count": record["person_count"] if record else 0,
        "company_count": record["company_count"] if record else 0,
        "health_count": record["health_count"] if record else 0,
        "finance_count": record["finance_count"] if record else 0,
        "contract_count": record["contract_count"] if record else 0,
        "sanction_count": record["sanction_count"] if record else 0,
        "election_count": record["election_count"] if record else 0,
        "amendment_count": record["amendment_count"] if record else 0,
        "embargo_count": record["embargo_count"] if record else 0,
        "education_count": record["education_count"] if record else 0,
        "convenio_count": record["convenio_count"] if record else 0,
        "laborstats_count": record["laborstats_count"] if record else 0,
        "offshore_entity_count": record["offshore_entity_count"] if record else 0,
        "offshore_officer_count": record["offshore_officer_count"] if record else 0,
        "global_pep_count": record["global_pep_count"] if record else 0,
        "cvm_proceeding_count": record["cvm_proceeding_count"] if record else 0,
        "expense_count": record["expense_count"] if record else 0,
        "pep_record_count": record["pep_record_count"] if record else 0,
        "expulsion_count": record["expulsion_count"] if record else 0,
        "leniency_count": record["leniency_count"] if record else 0,
        "international_sanction_count": record["international_sanction_count"] if record else 0,
        "gov_card_expense_count": record["gov_card_expense_count"] if record else 0,
        "gov_travel_count": record["gov_travel_count"] if record else 0,
        "bid_count": record["bid_count"] if record else 0,
        "fund_count": record["fund_count"] if record else 0,
        "dou_act_count": record["dou_act_count"] if record else 0,
        "tax_waiver_count": record["tax_waiver_count"] if record else 0,
        "municipal_finance_count": record["municipal_finance_count"] if record else 0,
        "declared_asset_count": record["declared_asset_count"] if record else 0,
        "party_membership_count": record["party_membership_count"] if record else 0,
        "barred_ngo_count": record["barred_ngo_count"] if record else 0,
        "bcb_penalty_count": record["bcb_penalty_count"] if record else 0,
        "labor_movement_count": record["labor_movement_count"] if record else 0,
        "legal_case_count": record["legal_case_count"] if record else 0,
        "cpi_count": record["cpi_count"] if record else 0,
        "data_sources": 41,
    }

    _stats_cache = result
    _stats_cache_time = time.monotonic()
    return result


@router.get("/sources")
async def list_sources() -> dict[str, list[dict[str, str]]]:
    return {
        "sources": [
            {"id": "cnpj", "name": "Receita Federal (CNPJ)", "frequency": "monthly"},
            {"id": "tse", "name": "Tribunal Superior Eleitoral", "frequency": "biennial"},
            {"id": "transparencia", "name": "Portal da Transparência", "frequency": "monthly"},
            {"id": "ceis", "name": "CEIS/CNEP/CEPIM/CEAF", "frequency": "monthly"},
            {"id": "cnes", "name": "CNES/DATASUS", "frequency": "monthly"},
            {"id": "bndes", "name": "BNDES (Empréstimos)", "frequency": "monthly"},
            {"id": "pgfn", "name": "PGFN (Dívida Ativa)", "frequency": "monthly"},
            {"id": "ibama", "name": "IBAMA (Embargos)", "frequency": "monthly"},
            {"id": "comprasnet", "name": "ComprasNet/PNCP", "frequency": "monthly"},
            {"id": "tcu", "name": "TCU (Sanções)", "frequency": "monthly"},
            {"id": "transferegov", "name": "TransfereGov (Convênios)", "frequency": "monthly"},
            {"id": "rais", "name": "RAIS (Estatísticas Trabalhistas)", "frequency": "annual"},
            {"id": "inep", "name": "INEP (Censo Educação)", "frequency": "annual"},
            {"id": "dou", "name": "Diário Oficial da União", "frequency": "daily"},
            {"id": "icij", "name": "ICIJ Offshore Leaks", "frequency": "yearly"},
            {"id": "opensanctions", "name": "OpenSanctions (PEPs globais)", "frequency": "monthly"},
            {"id": "cvm", "name": "CVM (Processos Sancionadores)", "frequency": "monthly"},
            {"id": "camara", "name": "Câmara dos Deputados (CEAP)", "frequency": "monthly"},
            {"id": "senado", "name": "Senado Federal (CEAPS)", "frequency": "monthly"},
            {"id": "pep_cgu", "name": "CGU PEP (Pessoas Expostas)", "frequency": "monthly"},
            {"id": "ceaf", "name": "CEAF (Servidores Expulsos)", "frequency": "monthly"},
            {"id": "leniency", "name": "Acordos de Leniência", "frequency": "monthly"},
            {"id": "ofac", "name": "OFAC SDN (Sanções Internacionais)", "frequency": "monthly"},
            {"id": "holdings", "name": "Brasil.IO (Holdings Empresariais)", "frequency": "monthly"},
            {"id": "cpgf", "name": "CPGF (Cartão de Pagamento)", "frequency": "monthly"},
            {"id": "viagens", "name": "Viagens a Serviço", "frequency": "monthly"},
            {"id": "siop", "name": "SIOP (Emendas Parlamentares)", "frequency": "annual"},
            {"id": "pncp", "name": "PNCP (Licitações)", "frequency": "monthly"},
            {"id": "cvm_funds", "name": "CVM (Fundos de Investimento)", "frequency": "monthly"},
            {"id": "renuncias", "name": "Renúncias Fiscais", "frequency": "annual"},
            {"id": "siconfi", "name": "SICONFI (Finanças Municipais)", "frequency": "annual"},
            {"id": "tse_bens", "name": "TSE Bens Declarados", "frequency": "biennial"},
            {"id": "tse_filiados", "name": "TSE Filiação Partidária", "frequency": "monthly"},
            {"id": "cepim", "name": "CEPIM (ONGs Impedidas)", "frequency": "monthly"},
            {"id": "bcb", "name": "BCB (Penalidades Bancárias)", "frequency": "monthly"},
            {"id": "caged", "name": "CAGED (Movimentações Trabalhistas)", "frequency": "monthly"},
            {"id": "stf", "name": "STF (Decisões Corte Aberta)", "frequency": "monthly"},
            {"id": "eu_sanctions", "name": "EU (Sanções Europeias)", "frequency": "monthly"},
            {
                "id": "un_sanctions",
                "name": "ONU (Sanções do Conselho de Segurança)",
                "frequency": "monthly",
            },
            {
                "id": "world_bank",
                "name": "Banco Mundial (Firmas Impedidas)",
                "frequency": "monthly",
            },
            {"id": "senado_cpis", "name": "Senado CPIs", "frequency": "yearly"},
        ]
    }
