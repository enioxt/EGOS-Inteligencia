"""Tests for X-Request-ID middleware."""

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from bracc.middleware.request_id import RequestIDMiddleware


async def _echo(request: Request) -> JSONResponse:
    return JSONResponse({"ok": True})


def _make_app() -> Starlette:
    app = Starlette(routes=[Route("/test", _echo)])
    app.add_middleware(RequestIDMiddleware)
    return app


@pytest.mark.anyio
async def test_generates_request_id():
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/test")
    assert resp.status_code == 200
    rid = resp.headers.get("x-request-id")
    assert rid is not None
    assert len(rid) == 12  # uuid4[:12]


@pytest.mark.anyio
async def test_echoes_client_request_id():
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/test", headers={"X-Request-ID": "my-custom-id"})
    assert resp.headers.get("x-request-id") == "my-custom-id"


@pytest.mark.anyio
async def test_unique_ids_per_request():
    app = _make_app()
    ids = []
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for _ in range(5):
            resp = await client.get("/test")
            ids.append(resp.headers["x-request-id"])
    assert len(set(ids)) == 5  # all unique
