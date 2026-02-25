from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_meta_sources(client: AsyncClient) -> None:
    response = await client.get("/api/v1/meta/sources")
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert len(data["sources"]) == 41
    source_ids = [s["id"] for s in data["sources"]]
    assert "cnpj" in source_ids
    assert "tse" in source_ids
    assert "bndes" in source_ids
    assert "pgfn" in source_ids
    assert "ibama" in source_ids
    assert "comprasnet" in source_ids
    assert "tcu" in source_ids
    assert "transferegov" in source_ids
    assert "rais" in source_ids
    assert "inep" in source_ids
    assert "dou" in source_ids
    assert "icij" in source_ids
    assert "opensanctions" in source_ids
    assert "cvm" in source_ids
    assert "camara" in source_ids
    assert "senado" in source_ids
    assert "pep_cgu" in source_ids
    assert "ceaf" in source_ids
    assert "leniency" in source_ids
    assert "ofac" in source_ids
    assert "holdings" in source_ids
    assert "cpgf" in source_ids
    assert "viagens" in source_ids
    assert "siop" in source_ids
    assert "pncp" in source_ids
    assert "cvm_funds" in source_ids
    assert "renuncias" in source_ids
    assert "siconfi" in source_ids
    assert "tse_bens" in source_ids
    assert "tse_filiados" in source_ids
    assert "cepim" in source_ids
    assert "bcb" in source_ids
    assert "caged" in source_ids
    assert "stf" in source_ids
    assert "eu_sanctions" in source_ids
    assert "un_sanctions" in source_ids
    assert "world_bank" in source_ids
    assert "senado_cpis" in source_ids


@pytest.mark.anyio
async def test_meta_stats(client: AsyncClient) -> None:
    mock_record = {
        "total_nodes": 87_500_000,
        "total_relationships": 53_100_000,
        "person_count": 2_450_000,
        "company_count": 58_500_000,
        "health_count": 602_000,
        "finance_count": 24_000_000,
        "contract_count": 1_080_000,
        "sanction_count": 69_000,
        "election_count": 17_000,
        "amendment_count": 98_000,
        "embargo_count": 79_000,
        "education_count": 224_000,
        "convenio_count": 67_000,
        "laborstats_count": 29_500,
        "offshore_entity_count": 810_000,
        "offshore_officer_count": 500_000,
        "global_pep_count": 15_000,
        "cvm_proceeding_count": 5_000,
        "expense_count": 2_000_000,
        "pep_record_count": 100_000,
        "expulsion_count": 10_000,
        "leniency_count": 34,
        "international_sanction_count": 12_000,
        "gov_card_expense_count": 500_000,
        "gov_travel_count": 150_000,
        "bid_count": 2_000_000,
        "fund_count": 30_000,
        "dou_act_count": 50_000,
        "tax_waiver_count": 800_000,
        "municipal_finance_count": 100_000,
        "declared_asset_count": 5_000_000,
        "party_membership_count": 15_000_000,
        "barred_ngo_count": 5_000,
        "bcb_penalty_count": 10_000,
        "labor_movement_count": 2_000_000,
        "legal_case_count": 100_000,
        "cpi_count": 500,
    }

    # Reset the stats cache between tests
    import icarus.routers.meta as meta_module
    meta_module._stats_cache = None
    meta_module._stats_cache_time = 0.0

    with patch(
        "icarus.routers.meta.execute_query_single",
        new_callable=AsyncMock,
        return_value=mock_record,
    ):
        response = await client.get("/api/v1/meta/stats")

    assert response.status_code == 200
    data = response.json()

    assert data["total_nodes"] == 87_500_000
    assert data["total_relationships"] == 53_100_000
    assert data["person_count"] == 2_450_000
    assert data["company_count"] == 58_500_000
    assert data["health_count"] == 602_000
    assert data["finance_count"] == 24_000_000
    assert data["contract_count"] == 1_080_000
    assert data["sanction_count"] == 69_000
    assert data["election_count"] == 17_000
    assert data["amendment_count"] == 98_000
    assert data["embargo_count"] == 79_000
    assert data["education_count"] == 224_000
    assert data["convenio_count"] == 67_000
    assert data["laborstats_count"] == 29_500
    assert data["offshore_entity_count"] == 810_000
    assert data["offshore_officer_count"] == 500_000
    assert data["global_pep_count"] == 15_000
    assert data["cvm_proceeding_count"] == 5_000
    assert data["expense_count"] == 2_000_000
    assert data["pep_record_count"] == 100_000
    assert data["expulsion_count"] == 10_000
    assert data["leniency_count"] == 34
    assert data["international_sanction_count"] == 12_000
    assert data["gov_card_expense_count"] == 500_000
    assert data["gov_travel_count"] == 150_000
    assert data["bid_count"] == 2_000_000
    assert data["fund_count"] == 30_000
    assert data["dou_act_count"] == 50_000
    assert data["tax_waiver_count"] == 800_000
    assert data["municipal_finance_count"] == 100_000
    assert data["declared_asset_count"] == 5_000_000
    assert data["party_membership_count"] == 15_000_000
    assert data["barred_ngo_count"] == 5_000
    assert data["bcb_penalty_count"] == 10_000
    assert data["labor_movement_count"] == 2_000_000
    assert data["legal_case_count"] == 100_000
    assert data["cpi_count"] == 500
    assert data["data_sources"] == 41
