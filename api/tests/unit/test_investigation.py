import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from bracc.models.investigation import (
    InvestigationExportBundle,
    InvestigationResponse,
)
from bracc.services import investigation_service
from bracc.services.neo4j_service import CypherLoader

FAKE_PDF = b"%PDF-1.4 fake pdf content for testing"

INVESTIGATION_CYPHER_FILES = [
    "investigation_create",
    "investigation_get",
    "investigation_list",
    "investigation_shared_count",
    "investigation_shared_list",
    "investigation_update",
    "investigation_delete",
    "investigation_add_entity",
    "investigation_remove_entity",
    "investigation_share",
    "investigation_by_token",
    "annotation_create",
    "annotation_list",
    "annotation_list_by_token",
    "annotation_delete",
    "tag_create",
    "tag_list",
    "tag_list_by_token",
    "tag_delete",
    "tag_add_to_entity",
]


def test_all_investigation_cypher_files_exist() -> None:
    for name in INVESTIGATION_CYPHER_FILES:
        try:
            CypherLoader.load(name)
        except FileNotFoundError:
            pytest.fail(f"Missing .cypher file: {name}.cypher")
        finally:
            CypherLoader.clear_cache()


def test_public_share_queries_are_bounded() -> None:
    for name in ("annotation_list_by_token", "tag_list_by_token"):
        try:
            cypher = CypherLoader.load(name)
        finally:
            CypherLoader.clear_cache()
        assert "LIMIT 1000" in cypher.upper(), f"{name}.cypher must be bounded"


def _mock_record(data: dict[str, object]) -> MagicMock:
    """Create a MagicMock that behaves like a neo4j.Record."""
    record = MagicMock()
    record.__getitem__ = lambda self, key: data[key]
    record.__contains__ = lambda self, key: key in data
    record.keys.return_value = list(data.keys())
    record.__iter__ = lambda self: iter(data.keys())
    return record


def _fake_result(records: list[MagicMock]) -> AsyncMock:
    """Create a mock Result that yields records."""
    result = AsyncMock()

    async def _iter(self: object) -> object:  # noqa: ANN001
        for r in records:
            yield r

    result.__aiter__ = _iter
    result.single = AsyncMock(return_value=records[0] if records else None)
    return result


def _setup_mock_session(
    driver: MagicMock,
    records: list[MagicMock],
) -> AsyncMock:
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(return_value=_fake_result(records))
    driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
    return mock_session


def _user_record() -> MagicMock:
    """Mock user record for auth dependency resolution."""
    return _mock_record({
        "id": "test-user-id",
        "email": "test@example.com",
        "created_at": "2026-01-01T00:00:00Z",
    })


def _setup_session_with_user_and_data(
    driver: MagicMock,
    data_record: MagicMock,
) -> AsyncMock:
    """Setup mock session that returns user record on first call, data on second."""
    user_rec = _user_record()
    mock_session = AsyncMock()
    call_count = 0

    async def _run_side_effect(*args: object, **kwargs: object) -> AsyncMock:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # user_get_by_id for auth
            return _fake_result([user_rec])
        return _fake_result([data_record])

    mock_session.run = AsyncMock(side_effect=_run_side_effect)
    driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
    return mock_session


def _setup_session_with_user_only(driver: MagicMock) -> AsyncMock:
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(return_value=_fake_result([_user_record()]))
    driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
    return mock_session


@pytest.mark.anyio
async def test_list_shared_investigations_preserves_total_on_empty_page() -> None:
    session = AsyncMock()
    total_record = _mock_record({"total": 3})

    with (
        patch.object(
            investigation_service,
            "execute_query_single",
            new=AsyncMock(return_value=total_record),
        ) as count_mock,
        patch.object(
            investigation_service,
            "execute_query",
            new=AsyncMock(return_value=[]),
        ) as list_mock,
    ):
        investigations, total = await investigation_service.list_shared_investigations(
            session,
            page=2,
            size=10,
        )

    assert investigations == []
    assert total == 3
    count_mock.assert_awaited_once_with(session, "investigation_shared_count")
    list_mock.assert_awaited_once_with(
        session,
        "investigation_shared_list",
        {"skip": 10, "limit": 10},
    )


@pytest.mark.anyio
async def test_get_by_share_token_masks_public_cpfs() -> None:
    session = AsyncMock()
    record = _mock_record({
        "id": "shared-id",
        "title": "Publica",
        "description": "desc",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "share_token": "token-1",
        "entity_ids": ["12345678901", "12345678000190"],
    })

    with patch.object(
        investigation_service,
        "execute_query_single",
        new=AsyncMock(return_value=record),
    ):
        investigation = await investigation_service.get_by_share_token(session, "token-1")

    assert investigation is not None
    assert investigation.entity_ids == ["***.***.***.01", "12345678000190"]


@pytest.mark.anyio
async def test_list_annotations_by_share_token_masks_public_cpfs() -> None:
    session = AsyncMock()
    record = _mock_record({
        "id": "ann-1",
        "entity_id": "12345678901",
        "investigation_id": "shared-id",
        "text": "nota",
        "created_at": "2026-01-01T00:00:00Z",
    })

    with patch.object(
        investigation_service,
        "execute_query",
        new=AsyncMock(return_value=[record]),
    ):
        annotations = await investigation_service.list_annotations_by_share_token(session, "token-1")

    assert annotations[0].entity_id == "***.***.***.01"


@pytest.mark.anyio
async def test_import_investigation_bundle_skips_annotations_for_unimported_entities() -> None:
    session = AsyncMock()
    created = InvestigationResponse(
        id="created-id",
        title="Investigacao importada",
        description="desc",
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
        entity_ids=[],
        share_token=None,
    )
    bundle = InvestigationExportBundle.model_validate({
        "investigation": {
            "id": "old-id",
            "title": "Investigacao importada",
            "description": "desc",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "entity_ids": ["missing-entity"],
            "share_token": None,
        },
        "annotations": [
            {
                "id": "ann-1",
                "entity_id": "missing-entity",
                "investigation_id": "old-id",
                "text": "nota",
                "created_at": "2026-01-01T00:00:00Z",
            }
        ],
        "tags": [],
    })

    with (
        patch.object(
            investigation_service,
            "create_investigation",
            new=AsyncMock(return_value=created),
        ),
        patch.object(
            investigation_service,
            "add_entity_to_investigation",
            new=AsyncMock(return_value=False),
        ),
        patch.object(
            investigation_service,
            "create_annotation",
            new=AsyncMock(),
        ) as create_annotation_mock,
        patch.object(
            investigation_service,
            "get_investigation",
            new=AsyncMock(return_value=created),
        ),
    ):
        result = await investigation_service.import_investigation_bundle(
            session,
            bundle,
            "user-1",
        )

    assert result.imported_entities == 0
    assert result.imported_annotations == 0
    assert result.skipped_entity_ids == ["missing-entity"]
    create_annotation_mock.assert_not_awaited()


@pytest.mark.anyio
async def test_create_investigation(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    record_data = {
        "id": "test-uuid",
        "title": "Test Investigation",
        "description": "",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "share_token": None,
        "entity_ids": [],
    }
    mock_record = _mock_record(record_data)

    from bracc.main import app

    _setup_session_with_user_and_data(app.state.neo4j_driver, mock_record)

    response = await client.post(
        "/api/v1/investigations/",
        json={"title": "Test Investigation"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Investigation"
    assert "id" in data


@pytest.mark.anyio
async def test_create_investigation_no_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/investigations/",
        json={"title": "Test Investigation"},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_list_investigations(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    record_data = {
        "total": 1,
        "id": "test-uuid",
        "title": "Test",
        "description": "",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "share_token": None,
        "entity_ids": [],
    }
    mock_record = _mock_record(record_data)
    user_rec = _user_record()

    from bracc.main import app

    driver = app.state.neo4j_driver
    mock_session = AsyncMock()

    call_count = 0

    async def _run_side_effect(*args: object, **kwargs: object) -> AsyncMock:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return _fake_result([user_rec])
        # list query returns records via __aiter__
        result = AsyncMock()

        async def _iter(self: object) -> object:  # noqa: ANN001
            yield mock_record

        result.__aiter__ = _iter
        result.single = AsyncMock(return_value=mock_record)
        return result

    mock_session.run = AsyncMock(side_effect=_run_side_effect)
    driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

    response = await client.get("/api/v1/investigations/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "investigations" in data
    assert "total" in data


@pytest.mark.anyio
async def test_get_investigation_no_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/investigations/some-id")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_get_nonexistent_investigation(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    from bracc.main import app

    user_rec = _user_record()
    driver = app.state.neo4j_driver
    mock_session = AsyncMock()

    call_count = 0

    async def _run_side_effect(*args: object, **kwargs: object) -> AsyncMock:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return _fake_result([user_rec])
        result = AsyncMock()

        async def _iter(self: object) -> object:  # noqa: ANN001
            return
            yield  # noqa: UP028

        result.__aiter__ = _iter
        result.single = AsyncMock(return_value=None)
        return result

    mock_session.run = AsyncMock(side_effect=_run_side_effect)
    driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

    response = await client.get(
        "/api/v1/investigations/nonexistent-id", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_list_annotations_no_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/investigations/inv-uuid/annotations")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_list_tags_no_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/investigations/inv-uuid/tags")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_delete_investigation(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    delete_record = _mock_record({"deleted": 1})

    from bracc.main import app

    _setup_session_with_user_and_data(app.state.neo4j_driver, delete_record)

    response = await client.delete(
        "/api/v1/investigations/test-uuid", headers=auth_headers
    )
    assert response.status_code == 204


@pytest.mark.anyio
async def test_delete_investigation_no_auth(client: AsyncClient) -> None:
    response = await client.delete("/api/v1/investigations/test-uuid")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_create_annotation(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    record_data = {
        "id": "ann-uuid",
        "entity_id": "entity-1",
        "investigation_id": "inv-uuid",
        "text": "Note about entity",
        "created_at": "2026-01-01T00:00:00Z",
    }
    mock_record = _mock_record(record_data)

    from bracc.main import app

    _setup_session_with_user_and_data(app.state.neo4j_driver, mock_record)

    response = await client.post(
        "/api/v1/investigations/inv-uuid/annotations",
        json={"entity_id": "entity-1", "text": "Note about entity"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Note about entity"


@pytest.mark.anyio
async def test_create_tag(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    record_data = {
        "id": "tag-uuid",
        "investigation_id": "inv-uuid",
        "name": "important",
        "color": "#E07A2F",
    }
    mock_record = _mock_record(record_data)

    from bracc.main import app

    _setup_session_with_user_and_data(app.state.neo4j_driver, mock_record)

    response = await client.post(
        "/api/v1/investigations/inv-uuid/tags",
        json={"name": "important"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "important"
    assert data["color"] == "#E07A2F"


@pytest.mark.anyio
async def test_share_investigation(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    record_data = {
        "id": "inv-uuid",
        "share_token": "share-token-uuid",
    }
    mock_record = _mock_record(record_data)

    from bracc.main import app

    _setup_session_with_user_and_data(app.state.neo4j_driver, mock_record)

    response = await client.post(
        "/api/v1/investigations/inv-uuid/share", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "share_token" in data


@pytest.mark.anyio
async def test_import_investigation_bundle(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    from bracc.main import app

    _setup_session_with_user_only(app.state.neo4j_driver)

    import_result = {
        "investigation": {
            "id": "imported-inv",
            "title": "Investigacao importada",
            "description": "desc",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "entity_ids": ["123"],
            "share_token": None,
        },
        "imported_entities": 1,
        "skipped_entity_ids": [],
        "imported_annotations": 1,
        "imported_tags": 1,
    }

    payload = {
        "investigation": {
            "id": "old-id",
            "title": "Investigacao importada",
            "description": "desc",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "entity_ids": ["123"],
            "share_token": "share-token",
        },
        "annotations": [
            {
                "id": "ann-1",
                "entity_id": "123",
                "investigation_id": "old-id",
                "text": "nota",
                "created_at": "2026-01-01T00:00:00Z",
            }
        ],
        "tags": [
            {
                "id": "tag-1",
                "investigation_id": "old-id",
                "name": "prioridade",
                "color": "#E07A2F",
            }
        ],
    }

    with patch(
        "bracc.routers.investigation.svc.import_investigation_bundle",
        new=AsyncMock(return_value=import_result),
    ) as import_mock:
        response = await client.post(
            "/api/v1/investigations/import",
            files={"file": ("investigation.json", json.dumps(payload), "application/json")},
            headers=auth_headers,
        )

    assert response.status_code == 201
    assert response.json()["investigation"]["id"] == "imported-inv"
    import_mock.assert_awaited_once()


@pytest.mark.anyio
async def test_import_investigation_rejects_non_json(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    from bracc.main import app

    _setup_session_with_user_only(app.state.neo4j_driver)

    response = await client.post(
        "/api/v1/investigations/import",
        files={"file": ("investigation.pdf", b"%PDF-1.4", "application/pdf")},
        headers=auth_headers,
    )

    assert response.status_code == 415


@pytest.mark.anyio
async def test_import_investigation_rejects_oversized_json(
    client: AsyncClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from bracc.main import app
    from bracc.routers import investigation as investigation_router

    _setup_session_with_user_only(app.state.neo4j_driver)
    monkeypatch.setattr(investigation_router.settings, "investigation_import_max_bytes", 16)

    response = await client.post(
        "/api/v1/investigations/import",
        files={
            "file": (
                "investigation.json",
                json.dumps({"payload": "x" * 32}),
                "application/json",
            )
        },
        headers=auth_headers,
    )

    assert response.status_code == 413


@pytest.mark.anyio
async def test_list_shared_investigations_public(
    client: AsyncClient,
) -> None:
    shared_response = {
        "investigations": [
            {
                "id": "shared-inv",
                "title": "Publica",
                "description": "desc",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-02T00:00:00Z",
                "entity_ids": ["123"],
                "share_token": "token-1",
            }
        ],
        "total": 1,
    }

    with patch(
        "bracc.routers.investigation.svc.list_shared_investigations",
        new=AsyncMock(return_value=(shared_response["investigations"], 1)),
    ):
        response = await client.get("/api/v1/shared")

    assert response.status_code == 200
    assert response.json() == shared_response


@pytest.mark.anyio
async def test_get_shared_investigation_includes_findings(
    client: AsyncClient,
) -> None:
    shared_response = {
        "id": "shared-inv",
        "title": "Publica",
        "description": "desc",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-02T00:00:00Z",
        "entity_ids": ["123"],
        "share_token": "token-1",
        "annotations": [
            {
                "id": "ann-1",
                "entity_id": "123",
                "investigation_id": "shared-inv",
                "text": "nota publica",
                "created_at": "2026-01-01T00:00:00Z",
            }
        ],
        "tags": [
            {
                "id": "tag-1",
                "investigation_id": "shared-inv",
                "name": "urgente",
                "color": "#E07A2F",
            }
        ],
    }

    with patch(
        "bracc.routers.investigation.svc.get_shared_investigation",
        new=AsyncMock(return_value=shared_response),
    ):
        response = await client.get("/api/v1/shared/token-1")

    assert response.status_code == 200
    data = response.json()
    assert data["annotations"][0]["text"] == "nota publica"
    assert data["tags"][0]["name"] == "urgente"


@pytest.mark.anyio
async def test_fork_shared_investigation(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    from bracc.main import app

    _setup_session_with_user_only(app.state.neo4j_driver)

    fork_response = {
        "investigation": {
            "id": "forked-inv",
            "title": "Publica (copy)",
            "description": "desc",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "entity_ids": ["123"],
            "share_token": None,
        },
        "imported_entities": 1,
        "skipped_entity_ids": [],
        "imported_annotations": 1,
        "imported_tags": 1,
    }

    with patch(
        "bracc.routers.investigation.svc.fork_shared_investigation",
        new=AsyncMock(return_value=fork_response),
    ) as fork_mock:
        response = await client.post(
            "/api/v1/shared/token-1/fork",
            json={"title": "Publica (copy)"},
            headers=auth_headers,
        )

    assert response.status_code == 201
    assert response.json()["investigation"]["id"] == "forked-inv"
    fork_mock.assert_awaited_once()


@pytest.mark.anyio
async def test_export_investigation(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    inv_record = _mock_record({
        "id": "inv-uuid",
        "title": "Test",
        "description": "",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "share_token": None,
        "entity_ids": [],
    })

    from bracc.main import app

    user_rec = _user_record()
    call_count = 0

    driver = app.state.neo4j_driver
    mock_session = AsyncMock()

    async def _run_side_effect(*args: object, **kwargs: object) -> AsyncMock:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return _fake_result([user_rec])
        if call_count == 2:
            # investigation_get
            return _fake_result([inv_record])
        # annotation_list / tag_list return empty
        result = AsyncMock()

        async def _empty_iter(self: object) -> object:  # noqa: ANN001
            return
            yield  # noqa: UP028

        result.__aiter__ = _empty_iter
        result.single = AsyncMock(return_value=None)
        return result

    mock_session.run = AsyncMock(side_effect=_run_side_effect)
    driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

    response = await client.get(
        "/api/v1/investigations/inv-uuid/export", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "investigation" in data
    assert "annotations" in data
    assert "tags" in data


@pytest.mark.anyio
async def test_export_investigation_no_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/investigations/inv-uuid/export")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_export_pdf_returns_pdf(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    inv_record = _mock_record({
        "id": "inv-uuid",
        "title": "Test",
        "description": "",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "share_token": None,
        "entity_ids": [],
    })

    from bracc.main import app

    user_rec = _user_record()
    driver = app.state.neo4j_driver
    mock_session = AsyncMock()

    call_count = 0

    async def _run_side_effect(*args: object, **kwargs: object) -> AsyncMock:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return _fake_result([user_rec])
        if call_count == 2:
            # investigation_get
            return _fake_result([inv_record])
        # annotation_list / tag_list return empty
        result = AsyncMock()

        async def _empty_iter(self: object) -> object:  # noqa: ANN001
            return
            yield  # noqa: UP028

        result.__aiter__ = _empty_iter
        result.single = AsyncMock(return_value=None)
        return result

    mock_session.run = AsyncMock(side_effect=_run_side_effect)
    driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

    mock_html_cls = MagicMock()
    mock_html_cls.return_value.write_pdf.return_value = FAKE_PDF
    fake_weasyprint = MagicMock()
    fake_weasyprint.HTML = mock_html_cls

    with patch.dict("sys.modules", {"weasyprint": fake_weasyprint}):
        response = await client.get(
            "/api/v1/investigations/inv-uuid/export/pdf", headers=auth_headers
        )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content[:5] == b"%PDF-"


@pytest.mark.anyio
async def test_export_pdf_not_found(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    from bracc.main import app

    user_rec = _user_record()
    driver = app.state.neo4j_driver
    mock_session = AsyncMock()

    call_count = 0

    async def _run_side_effect(*args: object, **kwargs: object) -> AsyncMock:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return _fake_result([user_rec])
        # investigation_get returns None
        result = AsyncMock()

        async def _empty_iter(self: object) -> object:  # noqa: ANN001
            return
            yield  # noqa: UP028

        result.__aiter__ = _empty_iter
        result.single = AsyncMock(return_value=None)
        return result

    mock_session.run = AsyncMock(side_effect=_run_side_effect)
    driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

    response = await client.get(
        "/api/v1/investigations/nonexistent/export/pdf", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_annotation(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    delete_record = _mock_record({"deleted": 1})

    from bracc.main import app

    _setup_session_with_user_and_data(app.state.neo4j_driver, delete_record)

    response = await client.delete(
        "/api/v1/investigations/inv-uuid/annotations/ann-uuid",
        headers=auth_headers,
    )
    assert response.status_code == 204


@pytest.mark.anyio
async def test_delete_annotation_not_found(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    delete_record = _mock_record({"deleted": 0})

    from bracc.main import app

    _setup_session_with_user_and_data(app.state.neo4j_driver, delete_record)

    response = await client.delete(
        "/api/v1/investigations/inv-uuid/annotations/nonexistent",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_annotation_no_auth(client: AsyncClient) -> None:
    response = await client.delete(
        "/api/v1/investigations/inv-uuid/annotations/ann-uuid"
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_delete_tag(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    delete_record = _mock_record({"deleted": 1})

    from bracc.main import app

    _setup_session_with_user_and_data(app.state.neo4j_driver, delete_record)

    response = await client.delete(
        "/api/v1/investigations/inv-uuid/tags/tag-uuid",
        headers=auth_headers,
    )
    assert response.status_code == 204


@pytest.mark.anyio
async def test_delete_tag_not_found(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    delete_record = _mock_record({"deleted": 0})

    from bracc.main import app

    _setup_session_with_user_and_data(app.state.neo4j_driver, delete_record)

    response = await client.delete(
        "/api/v1/investigations/inv-uuid/tags/nonexistent",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_tag_no_auth(client: AsyncClient) -> None:
    response = await client.delete(
        "/api/v1/investigations/inv-uuid/tags/tag-uuid"
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_remove_entity(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    delete_record = _mock_record({"deleted": 1})

    from bracc.main import app

    _setup_session_with_user_and_data(app.state.neo4j_driver, delete_record)

    response = await client.delete(
        "/api/v1/investigations/inv-uuid/entities/entity-1",
        headers=auth_headers,
    )
    assert response.status_code == 204


@pytest.mark.anyio
async def test_remove_entity_not_found(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    delete_record = _mock_record({"deleted": 0})

    from bracc.main import app

    _setup_session_with_user_and_data(app.state.neo4j_driver, delete_record)

    response = await client.delete(
        "/api/v1/investigations/inv-uuid/entities/nonexistent",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_remove_entity_no_auth(client: AsyncClient) -> None:
    response = await client.delete(
        "/api/v1/investigations/inv-uuid/entities/entity-1"
    )
    assert response.status_code == 401


# --- Cypher integrity tests for investigation queries ---


def test_investigation_update_coalesce_includes_all_entity_id_fields() -> None:
    """investigation_update.cypher coalesce chain must include all entity ID fields."""
    try:
        cypher = CypherLoader.load("investigation_update")
    finally:
        CypherLoader.clear_cache()

    required_fields = [
        "e.cpf", "e.cnpj", "e.contract_id", "e.sanction_id", "e.amendment_id",
        "e.cnes_code", "e.finance_id", "e.embargo_id", "e.school_id",
        "e.convenio_id", "e.stats_id",
    ]
    for field in required_fields:
        assert field in cypher, (
            f"investigation_update.cypher coalesce chain missing {field}"
        )


def test_investigation_add_entity_returns_entity_id() -> None:
    """investigation_add_entity.cypher RETURN clause must include entity_id."""
    try:
        cypher = CypherLoader.load("investigation_add_entity")
    finally:
        CypherLoader.clear_cache()

    # The RETURN clause should produce an entity_id column
    assert "entity_id" in cypher, (
        "investigation_add_entity.cypher does not return entity_id"
    )
    # Also check it uses the coalesce pattern for entity_id resolution
    assert "coalesce(" in cypher.lower(), (
        "investigation_add_entity.cypher does not use coalesce for entity_id"
    )


def test_investigation_remove_entity_returns_deleted_column() -> None:
    """investigation_remove_entity.cypher must return a 'deleted' column."""
    try:
        cypher = CypherLoader.load("investigation_remove_entity")
    finally:
        CypherLoader.clear_cache()

    assert "AS deleted" in cypher, (
        "investigation_remove_entity.cypher does not return 'deleted' column"
    )
