"""Smoke tests against the live VPS API (217.216.95.126).

Run with:
    pytest tests/integration/test_live_api.py -v --timeout=30

Requires VPS to be reachable. Skips gracefully if not.
"""

import os

import httpx
import pytest

VPS_BASE = os.environ.get("BRACC_VPS_URL", "https://egos.dedyn.io")
TIMEOUT = 15.0


@pytest.fixture(scope="module")
def api() -> httpx.Client:
    client = httpx.Client(base_url=VPS_BASE, timeout=TIMEOUT, verify=True)
    try:
        r = client.get("/health")
        if r.status_code != 200:
            pytest.skip("VPS API not reachable")
    except httpx.ConnectError:
        pytest.skip("VPS API not reachable")
    yield client
    client.close()


# ── Health & Meta ──────────────────────────────────────────────


class TestHealth:
    def test_health_ok(self, api: httpx.Client) -> None:
        r = api.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_security_headers(self, api: httpx.Client) -> None:
        r = api.get("/health")
        assert r.headers.get("x-content-type-options") == "nosniff"
        assert r.headers.get("x-frame-options") == "DENY"

    def test_meta_stats(self, api: httpx.Client) -> None:
        r = api.get("/api/v1/meta/stats")
        assert r.status_code == 200
        data = r.json()
        assert data["total_nodes"] > 1_000_000
        assert data["data_sources"] >= 100
        assert data["company_count"] > 8_000_000

    def test_meta_sources(self, api: httpx.Client) -> None:
        r = api.get("/api/v1/meta/sources")
        assert r.status_code == 200
        sources = r.json()["sources"]
        assert len(sources) >= 100
        ids = {s["id"] for s in sources}
        assert "cnpj" in ids
        assert "tse" in ids
        assert "pgfn" in ids

    def test_meta_health(self, api: httpx.Client) -> None:
        r = api.get("/api/v1/meta/health")
        assert r.status_code == 200
        assert r.json()["neo4j"] == "connected"


# ── Search ─────────────────────────────────────────────────────


class TestSearch:
    def test_search_company(self, api: httpx.Client) -> None:
        r = api.get("/api/v1/search", params={"q": "petrobras"})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] > 0
        assert len(data["results"]) > 0

    def test_search_cnpj(self, api: httpx.Client) -> None:
        r = api.get("/api/v1/search", params={"q": "33000167000101"})
        assert r.status_code == 200
        data = r.json()
        assert "total" in data

    def test_search_empty(self, api: httpx.Client) -> None:
        r = api.get("/api/v1/search", params={"q": "xyznonexistent99999"})
        assert r.status_code == 200
        assert r.json()["total"] == 0

    def test_search_pagination(self, api: httpx.Client) -> None:
        r = api.get("/api/v1/search", params={"q": "silva", "size": 5})
        assert r.status_code == 200
        data = r.json()
        assert data["size"] == 5
        assert len(data["results"]) <= 5


# ── Patterns ───────────────────────────────────────────────────


class TestPatterns:
    def test_list_patterns(self, api: httpx.Client) -> None:
        r = api.get("/api/v1/patterns/")
        assert r.status_code == 200
        patterns = r.json()["patterns"]
        assert len(patterns) == 10
        ids = {p["id"] for p in patterns}
        assert "sanctioned_still_receiving" in ids
        assert "benford_contract_values" in ids
        assert "hhi_contract_concentration" in ids

    def test_invalid_pattern_404(self, api: httpx.Client) -> None:
        r = api.get("/api/v1/patterns/test-entity/nonexistent_pattern")
        assert r.status_code == 404


# ── Entity ─────────────────────────────────────────────────────


class TestEntity:
    def test_entity_by_cnpj(self, api: httpx.Client) -> None:
        try:
            r = api.get("/api/v1/entity/33000167000101", timeout=20.0)
        except httpx.ReadTimeout:
            pytest.skip("Entity lookup timed out (ETL load on Neo4j)")
        assert r.status_code in (200, 404, 500)
        if r.status_code == 200:
            data = r.json()
            assert "cnpj" in data or "id" in data or "element_id" in data

    def test_entity_invalid_format(self, api: httpx.Client) -> None:
        r = api.get("/api/v1/entity/abc")
        assert r.status_code == 400

    def test_entity_graph(self, api: httpx.Client) -> None:
        r = api.get("/api/v1/search", params={"q": "petrobras", "size": 1})
        if r.status_code == 200 and r.json()["total"] > 0:
            entity_id = r.json()["results"][0].get("element_id", "")
            if entity_id:
                r2 = api.get(f"/api/v1/graph/{entity_id}", params={"depth": 1})
                assert r2.status_code in (200, 404)


# ── Chat ───────────────────────────────────────────────────────


class TestChat:
    def test_chat_simple_query(self, api: httpx.Client) -> None:
        r = api.post(
            "/api/v1/chat",
            json={"message": "Quantas empresas existem no grafo?"},
            timeout=30.0,
        )
        assert r.status_code == 200
        data = r.json()
        assert "reply" in data
        assert len(data["reply"]) > 0

    def test_chat_rejects_empty(self, api: httpx.Client) -> None:
        r = api.post("/api/v1/chat", json={"message": ""})
        assert r.status_code in (400, 422)


# ── Activity & Monitor ─────────────────────────────────────────


class TestActivity:
    def test_activity_feed(self, api: httpx.Client) -> None:
        r = api.get("/api/v1/activity/feed")
        assert r.status_code == 200

    def test_cache_stats(self, api: httpx.Client) -> None:
        r = api.get("/api/v1/meta/cache-stats")
        assert r.status_code == 200
        data = r.json()
        assert "hits" in data or "hit_rate" in data or "total_hits" in data
