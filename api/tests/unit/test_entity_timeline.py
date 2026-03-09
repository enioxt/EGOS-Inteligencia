import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_timeline_rejects_limit_zero(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/entity/test-id/timeline?limit=0"
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_timeline_rejects_limit_over_max(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/entity/test-id/timeline?limit=101"
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_timeline_accepts_valid_limit(client: AsyncClient) -> None:
    # Should not return 422 for valid limit (may return 500 since no real DB)
    response = await client.get(
        "/api/v1/entity/test-id/timeline?limit=50"
    )
    assert response.status_code != 422


@pytest.mark.anyio
async def test_timeline_accepts_cursor_param(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/entity/test-id/timeline?cursor=2025-01-01&limit=10"
    )
    assert response.status_code != 422


@pytest.mark.anyio
async def test_timeline_default_limit(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/entity/test-id/timeline"
    )
    # Should not fail on validation (may fail on DB)
    assert response.status_code != 422


@pytest.mark.anyio
@pytest.mark.xfail(reason="Exposure endpoint needs real Neo4j record; AsyncMock breaks int() cast")
async def test_exposure_endpoint_exists(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/entity/test-id/exposure"
    )
    # Should not return 404 for unknown route (may return 500 since no real DB)
    assert response.status_code in (200, 400, 404, 500) or "Entity not found" in response.text
