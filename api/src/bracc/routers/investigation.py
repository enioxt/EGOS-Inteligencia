import json
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from neo4j import AsyncSession
from pydantic import ValidationError

from bracc.config import settings
from bracc.constants import PEP_ROLES
from bracc.dependencies import CurrentUser, get_session
from bracc.middleware.cpf_masking import mask_formatted_cpf, mask_raw_cpf
from bracc.models.investigation import (
    Annotation,
    AnnotationCreate,
    InvestigationCreate,
    InvestigationExportBundle,
    InvestigationForkRequest,
    InvestigationImportResponse,
    InvestigationListResponse,
    InvestigationResponse,
    InvestigationUpdate,
    SharedInvestigationResponse,
    Tag,
    TagCreate,
)
from bracc.services import investigation_service as svc
from bracc.services.export_service import render_investigation_html, render_investigation_md
from bracc.services.neo4j_service import execute_query_single
from bracc.services.pdf_service import render_investigation_pdf
from bracc.services.public_guard import ensure_investigations_enabled

router = APIRouter(
    prefix="/api/v1/investigations",
    tags=["investigations"],
    dependencies=[Depends(ensure_investigations_enabled)],
)
shared_router = APIRouter(
    tags=["shared"],
    dependencies=[Depends(ensure_investigations_enabled)],
)


@router.post(
    "/",
    response_model=InvestigationResponse,
    status_code=201,
)
async def create_investigation(
    body: InvestigationCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
) -> InvestigationResponse:
    return await svc.create_investigation(session, body.title, body.description, user.id)


@router.get("/", response_model=InvestigationListResponse)
async def list_investigations(
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> InvestigationListResponse:
    investigations, total = await svc.list_investigations(session, page, size, user.id)
    return InvestigationListResponse(investigations=investigations, total=total)


@router.post(
    "/import",
    response_model=InvestigationImportResponse,
    status_code=201,
)
async def import_investigation(
    file: Annotated[UploadFile, File(...)],
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
) -> InvestigationImportResponse:
    filename = (file.filename or "").lower()
    content_type = (file.content_type or "").lower()
    if not filename.endswith(".json") and content_type not in {
        "application/json",
        "text/json",
    }:
        raise HTTPException(
            status_code=415,
            detail="Investigation import currently supports exported JSON bundles only",
        )

    raw = await file.read(settings.investigation_import_max_bytes + 1)
    if len(raw) > settings.investigation_import_max_bytes:
        raise HTTPException(
            status_code=413,
            detail="Investigation import file is too large",
        )
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=400, detail="Invalid investigation JSON file") from exc

    try:
        bundle = InvestigationExportBundle.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return await svc.import_investigation_bundle(session, bundle, user.id)


@router.get(
    "/{investigation_id}",
    response_model=InvestigationResponse,
)
async def get_investigation(
    investigation_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
) -> InvestigationResponse:
    result = await svc.get_investigation(session, investigation_id, user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return result


@router.patch(
    "/{investigation_id}",
    response_model=InvestigationResponse,
)
async def update_investigation(
    investigation_id: str,
    body: InvestigationUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
) -> InvestigationResponse:
    result = await svc.update_investigation(
        session, investigation_id, body.title, body.description, user.id
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return result


@router.delete(
    "/{investigation_id}",
    status_code=204,
)
async def delete_investigation(
    investigation_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
) -> None:
    deleted = await svc.delete_investigation(session, investigation_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Investigation not found")


@router.post(
    "/{investigation_id}/entities/{entity_id}",
    status_code=201,
)
async def add_entity(
    investigation_id: str,
    entity_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
) -> dict[str, str]:
    added = await svc.add_entity_to_investigation(
        session, investigation_id, entity_id, user.id
    )
    if not added:
        raise HTTPException(status_code=404, detail="Investigation or entity not found")
    return {"investigation_id": investigation_id, "entity_id": entity_id}


@router.post(
    "/{investigation_id}/annotations",
    response_model=Annotation,
    status_code=201,
)
async def create_annotation(
    investigation_id: str,
    body: AnnotationCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
) -> Annotation:
    return await svc.create_annotation(
        session, investigation_id, body.entity_id, body.text, user.id
    )


@router.get(
    "/{investigation_id}/annotations",
    response_model=list[Annotation],
)
async def list_annotations(
    investigation_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
) -> list[Annotation]:
    return await svc.list_annotations(session, investigation_id, user.id)


@router.post(
    "/{investigation_id}/tags",
    response_model=Tag,
    status_code=201,
)
async def create_tag(
    investigation_id: str,
    body: TagCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
) -> Tag:
    return await svc.create_tag(session, investigation_id, body.name, body.color, user.id)


@router.get(
    "/{investigation_id}/tags",
    response_model=list[Tag],
)
async def list_tags(
    investigation_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
) -> list[Tag]:
    return await svc.list_tags(session, investigation_id, user.id)


@router.delete(
    "/{investigation_id}/entities/{entity_id}",
    status_code=204,
)
async def remove_entity(
    investigation_id: str,
    entity_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
) -> None:
    removed = await svc.remove_entity_from_investigation(
        session, investigation_id, entity_id, user.id
    )
    if not removed:
        raise HTTPException(status_code=404, detail="Investigation or entity not found")


@router.delete(
    "/{investigation_id}/annotations/{annotation_id}",
    status_code=204,
)
async def delete_annotation(
    investigation_id: str,
    annotation_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
) -> None:
    deleted = await svc.delete_annotation(session, investigation_id, annotation_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Annotation not found")


@router.delete(
    "/{investigation_id}/tags/{tag_id}",
    status_code=204,
)
async def delete_tag(
    investigation_id: str,
    tag_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
) -> None:
    deleted = await svc.delete_tag(session, investigation_id, tag_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tag not found")


@router.post(
    "/{investigation_id}/share",
    response_model=dict[str, str],
)
async def generate_share_link(
    investigation_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
) -> dict[str, str]:
    token = await svc.generate_share_token(session, investigation_id, user.id)
    if token is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return {"share_token": token}


@shared_router.get("/api/v1/shared", response_model=InvestigationListResponse)
async def list_shared_investigations(
    session: Annotated[AsyncSession, Depends(get_session)],
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> InvestigationListResponse:
    investigations, total = await svc.list_shared_investigations(session, page, size)
    return InvestigationListResponse(investigations=investigations, total=total)


@shared_router.post(
    "/api/v1/shared/{token}/fork",
    response_model=InvestigationImportResponse,
    status_code=201,
)
async def fork_shared_investigation(
    token: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
    body: InvestigationForkRequest | None = None,
) -> InvestigationImportResponse:
    title = body.title if body else None
    result = await svc.fork_shared_investigation(session, token, user.id, title)
    if result is None:
        raise HTTPException(status_code=404, detail="Shared investigation not found")
    return result


@shared_router.get("/api/v1/shared/{token}", response_model=SharedInvestigationResponse)
async def get_shared_investigation(
    token: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SharedInvestigationResponse:
    result = await svc.get_shared_investigation(session, token)
    if result is None:
        raise HTTPException(status_code=404, detail="Shared investigation not found")
    return result


@router.get("/{investigation_id}/export", response_model=InvestigationExportBundle)
async def export_investigation(
    investigation_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
) -> InvestigationExportBundle:
    investigation = await svc.get_investigation(session, investigation_id, user.id)
    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")

    annotations = await svc.list_annotations(session, investigation_id, user.id)
    tags = await svc.list_tags(session, investigation_id, user.id)

    return InvestigationExportBundle(
        investigation=investigation,
        annotations=annotations,
        tags=tags,
    )


@router.get("/{investigation_id}/export/pdf")
async def export_investigation_pdf(
    investigation_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
    lang: Annotated[Literal["pt", "en"], Query()] = "pt",
) -> Response:
    investigation = await svc.get_investigation(session, investigation_id, user.id)
    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")

    annotations = await svc.list_annotations(session, investigation_id, user.id)
    tags = await svc.list_tags(session, investigation_id, user.id)

    entities: list[dict[str, str]] = []
    for entity_id in investigation.entity_ids:
        record = await execute_query_single(session, "entity_by_id", {"id": entity_id})
        if record is not None:
            node = record["e"]
            labels = record["entity_labels"]
            document = str(node.get("cpf", node.get("cnpj", "")))

            # CB-SEC-04: Mask non-PEP CPFs in PDF export (middleware only covers JSON)
            cpf_val = node.get("cpf")
            if cpf_val and isinstance(cpf_val, str):
                role = str(node.get("role", node.get("cargo", ""))).lower()
                is_pep = role in PEP_ROLES
                if not is_pep:
                    if "." in document and "-" in document:
                        document = mask_formatted_cpf(document)
                    elif len(document) == 11 and document.isdigit():
                        document = mask_raw_cpf(document)

            entities.append({
                "name": str(node.get("name", "")),
                "type": labels[0] if labels else "",
                "document": document,
            })

    pdf_bytes = await render_investigation_pdf(
        investigation, annotations, tags, entities, lang=lang
    )

    safe_title = "".join(c for c in investigation.title if c.isalnum() or c in " _-")[:100]
    filename = f"{safe_title or 'investigation'}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


async def _resolve_entities(
    session: "AsyncSession",
    entity_ids: list[str],
    user_id: str,
) -> list[dict[str, str]]:
    """Resolve entity IDs to name/type/document dicts with CPF masking."""
    entities: list[dict[str, str]] = []
    for entity_id in entity_ids:
        record = await execute_query_single(session, "entity_by_id", {"id": entity_id})
        if record is not None:
            node = record["e"]
            labels = record["entity_labels"]
            document = str(node.get("cpf", node.get("cnpj", "")))

            cpf_val = node.get("cpf")
            if cpf_val and isinstance(cpf_val, str):
                role = str(node.get("role", node.get("cargo", ""))).lower()
                is_pep = role in PEP_ROLES
                if not is_pep:
                    if "." in document and "-" in document:
                        document = mask_formatted_cpf(document)
                    elif len(document) == 11 and document.isdigit():
                        document = mask_raw_cpf(document)

            entities.append({
                "name": str(node.get("name", "")),
                "type": labels[0] if labels else "",
                "document": document,
            })
    return entities


@router.get("/{investigation_id}/export/md")
async def export_investigation_md(
    investigation_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
    lang: Annotated[Literal["pt", "en"], Query()] = "pt",
) -> Response:
    investigation = await svc.get_investigation(session, investigation_id, user.id)
    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")

    annotations = await svc.list_annotations(session, investigation_id, user.id)
    tags = await svc.list_tags(session, investigation_id, user.id)
    entities = await _resolve_entities(session, investigation.entity_ids, user.id)

    md_content = render_investigation_md(investigation, annotations, tags, entities, lang=lang)
    safe_title = "".join(c for c in investigation.title if c.isalnum() or c in " _-")[:100]
    filename = f"{safe_title or 'investigation'}.md"
    return Response(
        content=md_content,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{investigation_id}/export/html")
async def export_investigation_html(
    investigation_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: CurrentUser,
    lang: Annotated[Literal["pt", "en"], Query()] = "pt",
) -> Response:
    investigation = await svc.get_investigation(session, investigation_id, user.id)
    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")

    annotations = await svc.list_annotations(session, investigation_id, user.id)
    tags = await svc.list_tags(session, investigation_id, user.id)
    entities = await _resolve_entities(session, investigation.entity_ids, user.id)

    html_content = render_investigation_html(investigation, annotations, tags, entities, lang=lang)
    safe_title = "".join(c for c in investigation.title if c.isalnum() or c in " _-")[:100]
    filename = f"{safe_title or 'investigation'}.html"
    return Response(
        content=html_content,
        media_type="text/html; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
