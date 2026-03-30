import copy
import json
from typing import Any
from unittest.mock import AsyncMock

import httpx
import pytest

from bracc.config import settings
from bracc.routers import chat


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict[str, Any] | None = None) -> None:
        self.status_code = status_code
        self._payload = payload or {}
        self.request = httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")
        self.text = json.dumps(self._payload)

    def json(self) -> dict[str, Any]:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}",
                request=self.request,
                response=self,
            )


class _FakeAsyncClient:
    def __init__(self, responses: list[_FakeResponse]) -> None:
        self._responses = list(responses)
        self.requests: list[dict[str, Any]] = []

    async def __aenter__(self) -> "_FakeAsyncClient":
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    async def post(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> _FakeResponse:
        self.requests.append({
            "url": url,
            "headers": copy.deepcopy(headers),
            "json": copy.deepcopy(json),
        })
        if not self._responses:
            raise AssertionError("Unexpected extra OpenRouter call")
        return self._responses.pop(0)


@pytest.fixture(autouse=True)
def _reset_chat_state(monkeypatch: pytest.MonkeyPatch) -> None:
    chat._conversations.clear()
    chat._conversation_ts.clear()
    chat._usage_counts.clear()
    chat._usage_day.clear()
    chat.limiter._storage.reset()
    monkeypatch.setattr(chat, "_CREDIT_EXHAUSTED", False)
    monkeypatch.setattr(settings, "openrouter_api_key", "platform-key")


@pytest.mark.anyio
async def test_call_openrouter_executes_tool_calls_and_collects_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = _FakeAsyncClient(
        [
            _FakeResponse(
                200,
                {
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "tool_calls": [{
                                "id": "tool-1",
                                "function": {
                                    "name": "web_search",
                                    "arguments": json.dumps(
                                        {"query": "empresa teste", "max_results": 2}
                                    ),
                                },
                            }],
                        }
                    }],
                    "usage": {"prompt_tokens": 120, "completion_tokens": 30},
                },
            ),
            _FakeResponse(
                200,
                {
                    "choices": [{"message": {"content": "Resumo final com fontes"}}],
                    "usage": {"prompt_tokens": 60, "completion_tokens": 15},
                },
            ),
        ]
    )
    web_search = AsyncMock(
        return_value=[{
            "title": "Resultado 1",
            "url": "https://example.com",
            "snippet": "Trecho",
        }]
    )

    monkeypatch.setattr(chat.httpx, "AsyncClient", lambda timeout=45.0: fake_client)
    monkeypatch.setattr(chat, "tool_web_search", web_search)

    reply, entities, evidence, cost = await chat._call_openrouter(
        [{"role": "user", "content": "Busque por empresa teste"}],
        AsyncMock(),
        model=chat.MODEL_PREMIUM,
        api_key="test-key",
    )

    assert reply == "Resumo final com fontes"
    assert entities == []
    assert cost > 0
    web_search.assert_awaited_once_with("empresa teste", 2)
    assert len(evidence) == 1
    assert evidence[0]["tool"] == "web_search"
    assert evidence[0]["source"] == "Brave Search / DuckDuckGo"
    assert evidence[0]["result_count"] == 1
    assert fake_client.requests[0]["json"]["model"] == chat.MODEL_PREMIUM


@pytest.mark.anyio
async def test_call_openrouter_retries_with_free_model_after_credit_exhaustion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = _FakeAsyncClient(
        [
            _FakeResponse(429, {"error": {"message": "rate limited"}}),
            _FakeResponse(
                200,
                {
                    "choices": [{"message": {"content": "Resposta via fallback"}}],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 5},
                },
            ),
        ]
    )

    monkeypatch.setattr(chat.httpx, "AsyncClient", lambda timeout=45.0: fake_client)

    reply, entities, evidence, cost = await chat._call_openrouter(
        [{"role": "user", "content": "Resumo"}],
        AsyncMock(),
        model=chat.MODEL_PREMIUM,
        api_key="test-key",
    )

    assert reply == "Resposta via fallback"
    assert entities == []
    assert evidence == []
    assert cost > 0
    assert chat._CREDIT_EXHAUSTED is True
    assert fake_client.requests[0]["json"]["model"] == chat.MODEL_PREMIUM
    assert fake_client.requests[1]["json"]["model"] == chat.MODEL_FALLBACK


@pytest.mark.anyio
async def test_select_model_prefers_byok_key() -> None:
    model, api_key, tier = await chat._select_model("client-1", "user-key")

    assert model == chat.MODEL_PREMIUM
    assert api_key == "user-key"
    assert tier == "byok"


@pytest.mark.anyio
async def test_select_model_marks_limit_reached(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(chat, "_get_usage", AsyncMock(return_value=chat._TIER_FREE_LIMIT))

    model, api_key, tier = await chat._select_model("client-1")

    assert model == chat.MODEL_FREE
    assert api_key == settings.openrouter_api_key
    assert tier == "limite_atingido"


@pytest.mark.anyio
async def test_chat_endpoint_appends_daily_limit_notice(
    client: httpx.AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        chat,
        "_select_model",
        AsyncMock(return_value=(chat.MODEL_FREE, "test-key", "limite_atingido")),
    )
    monkeypatch.setattr(
        chat,
        "_call_openrouter",
        AsyncMock(return_value=("Resposta base", [], [], 0.12)),
    )
    monkeypatch.setattr(chat, "_increment_usage", AsyncMock(return_value=chat._TIER_FREE_LIMIT + 1))
    monkeypatch.setattr(chat, "log_activity", lambda *args, **kwargs: None)

    response = await client.post("/api/v1/chat", json={"message": "Quais dados existem?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["cost_usd"] == 0.12
    assert "Resposta base" in payload["reply"]
    assert "Limite diário atingido" in payload["reply"]


@pytest.mark.anyio
async def test_chat_endpoint_enforces_http_rate_limit(
    client: httpx.AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        chat,
        "_select_model",
        AsyncMock(return_value=(chat.MODEL_FREE, "test-key", "premium (30 restantes)")),
    )
    monkeypatch.setattr(
        chat,
        "_call_openrouter",
        AsyncMock(return_value=("Resposta base", [], [], 0.0)),
    )
    monkeypatch.setattr(chat, "_increment_usage", AsyncMock(return_value=1))
    monkeypatch.setattr(chat, "log_activity", lambda *args, **kwargs: None)

    for _ in range(30):
        response = await client.post("/api/v1/chat", json={"message": "Quais dados existem?"})
        assert response.status_code == 200

    blocked = await client.post("/api/v1/chat", json={"message": "Quais dados existem?"})

    assert blocked.status_code == 429
