import re
import uuid

from neo4j import AsyncSession, Record

from bracc.models.investigation import (
    Annotation,
    InvestigationExportBundle,
    InvestigationImportResponse,
    InvestigationResponse,
    SharedInvestigationResponse,
    Tag,
)
from bracc.services.neo4j_service import execute_query, execute_query_single


def _str(value: object) -> str:
    """Coerce Neo4j temporal or other types to string."""
    return str(value) if value is not None else ""


def _mask_public_entity_identifier(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) != 11:
        return value
    return f"***.***.***.{digits[-2:]}"


def _mask_public_investigation(investigation: InvestigationResponse) -> InvestigationResponse:
    return investigation.model_copy(
        update={
            "entity_ids": [
                _mask_public_entity_identifier(str(entity_id))
                for entity_id in investigation.entity_ids
            ]
        }
    )


def _mask_public_annotation(annotation: Annotation) -> Annotation:
    return annotation.model_copy(
        update={"entity_id": _mask_public_entity_identifier(annotation.entity_id)}
    )


def _record_to_investigation(record: Record) -> InvestigationResponse:
    """Convert a Neo4j Record to InvestigationResponse."""
    return InvestigationResponse(
        id=record["id"],
        title=record["title"],
        description=record["description"],
        created_at=_str(record["created_at"]),
        updated_at=_str(record["updated_at"]),
        entity_ids=record["entity_ids"],
        share_token=record["share_token"],
    )


def _record_to_annotation(record: Record) -> Annotation:
    return Annotation(
        id=record["id"],
        entity_id=record["entity_id"],
        investigation_id=record["investigation_id"],
        text=record["text"],
        created_at=_str(record["created_at"]),
    )


def _record_to_tag(record: Record) -> Tag:
    return Tag(
        id=record["id"],
        investigation_id=record["investigation_id"],
        name=record["name"],
        color=record["color"],
    )


async def create_investigation(
    session: AsyncSession,
    title: str,
    description: str | None,
    user_id: str,
) -> InvestigationResponse:
    record = await execute_query_single(
        session,
        "investigation_create",
        {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description or "",
            "user_id": user_id,
        },
    )
    if record is None:
        msg = "Failed to create investigation"
        raise RuntimeError(msg)
    return _record_to_investigation(record)


async def get_investigation(
    session: AsyncSession,
    investigation_id: str,
    user_id: str,
) -> InvestigationResponse | None:
    record = await execute_query_single(
        session,
        "investigation_get",
        {"id": investigation_id, "user_id": user_id},
    )
    if record is None:
        return None
    return _record_to_investigation(record)


async def list_investigations(
    session: AsyncSession,
    page: int,
    size: int,
    user_id: str,
) -> tuple[list[InvestigationResponse], int]:
    skip = (page - 1) * size
    records = await execute_query(
        session,
        "investigation_list",
        {"skip": skip, "limit": size, "user_id": user_id},
    )
    if not records:
        return [], 0
    total = int(records[0]["total"])
    investigations = [_record_to_investigation(r) for r in records]
    return investigations, total


async def update_investigation(
    session: AsyncSession,
    investigation_id: str,
    title: str | None,
    description: str | None,
    user_id: str,
) -> InvestigationResponse | None:
    record = await execute_query_single(
        session,
        "investigation_update",
        {"id": investigation_id, "title": title, "description": description, "user_id": user_id},
    )
    if record is None:
        return None
    return _record_to_investigation(record)


async def delete_investigation(
    session: AsyncSession,
    investigation_id: str,
    user_id: str,
) -> bool:
    record = await execute_query_single(
        session,
        "investigation_delete",
        {"id": investigation_id, "user_id": user_id},
    )
    if record is None:
        return False
    return int(record["deleted"]) > 0


async def add_entity_to_investigation(
    session: AsyncSession,
    investigation_id: str,
    entity_id: str,
    user_id: str,
) -> bool:
    record = await execute_query_single(
        session,
        "investigation_add_entity",
        {"investigation_id": investigation_id, "entity_id": entity_id, "user_id": user_id},
    )
    return record is not None


async def create_annotation(
    session: AsyncSession,
    investigation_id: str,
    entity_id: str,
    text: str,
    user_id: str,
) -> Annotation:
    record = await execute_query_single(
        session,
        "annotation_create",
        {
            "id": str(uuid.uuid4()),
            "investigation_id": investigation_id,
            "entity_id": entity_id,
            "text": text,
            "user_id": user_id,
        },
    )
    if record is None:
        msg = "Failed to create annotation"
        raise RuntimeError(msg)
    return _record_to_annotation(record)


async def list_annotations(
    session: AsyncSession,
    investigation_id: str,
    user_id: str,
) -> list[Annotation]:
    records = await execute_query(
        session,
        "annotation_list",
        {"investigation_id": investigation_id, "user_id": user_id},
    )
    return [_record_to_annotation(r) for r in records]


async def create_tag(
    session: AsyncSession,
    investigation_id: str,
    name: str,
    color: str,
    user_id: str,
) -> Tag:
    record = await execute_query_single(
        session,
        "tag_create",
        {
            "id": str(uuid.uuid4()),
            "investigation_id": investigation_id,
            "name": name,
            "color": color,
            "user_id": user_id,
        },
    )
    if record is None:
        msg = "Failed to create tag"
        raise RuntimeError(msg)
    return _record_to_tag(record)


async def list_tags(
    session: AsyncSession,
    investigation_id: str,
    user_id: str,
) -> list[Tag]:
    records = await execute_query(
        session,
        "tag_list",
        {"investigation_id": investigation_id, "user_id": user_id},
    )
    return [_record_to_tag(r) for r in records]


async def delete_annotation(
    session: AsyncSession,
    investigation_id: str,
    annotation_id: str,
    user_id: str,
) -> bool:
    record = await execute_query_single(
        session,
        "annotation_delete",
        {"investigation_id": investigation_id, "annotation_id": annotation_id, "user_id": user_id},
    )
    if record is None:
        return False
    return int(record["deleted"]) > 0


async def delete_tag(
    session: AsyncSession,
    investigation_id: str,
    tag_id: str,
    user_id: str,
) -> bool:
    record = await execute_query_single(
        session,
        "tag_delete",
        {"investigation_id": investigation_id, "tag_id": tag_id, "user_id": user_id},
    )
    if record is None:
        return False
    return int(record["deleted"]) > 0


async def remove_entity_from_investigation(
    session: AsyncSession,
    investigation_id: str,
    entity_id: str,
    user_id: str,
) -> bool:
    record = await execute_query_single(
        session,
        "investigation_remove_entity",
        {"investigation_id": investigation_id, "entity_id": entity_id, "user_id": user_id},
    )
    if record is None:
        return False
    return int(record["deleted"]) > 0


async def generate_share_token(
    session: AsyncSession,
    investigation_id: str,
    user_id: str,
) -> str | None:
    token = str(uuid.uuid4())
    record = await execute_query_single(
        session,
        "investigation_share",
        {"id": investigation_id, "share_token": token, "user_id": user_id},
    )
    if record is None:
        return None
    return str(record["share_token"])


async def get_by_share_token(
    session: AsyncSession,
    token: str,
) -> InvestigationResponse | None:
    record = await execute_query_single(
        session,
        "investigation_by_token",
        {"token": token},
    )
    if record is None:
        return None
    return _mask_public_investigation(_record_to_investigation(record))


async def list_shared_investigations(
    session: AsyncSession,
    page: int,
    size: int,
) -> tuple[list[InvestigationResponse], int]:
    skip = (page - 1) * size
    total_record = await execute_query_single(session, "investigation_shared_count")
    total = int(total_record["total"]) if total_record is not None else 0
    records = await execute_query(
        session,
        "investigation_shared_list",
        {"skip": skip, "limit": size},
    )
    if not records:
        return [], total
    investigations = [_mask_public_investigation(_record_to_investigation(r)) for r in records]
    return investigations, total


async def list_annotations_by_share_token(
    session: AsyncSession,
    token: str,
) -> list[Annotation]:
    records = await execute_query(session, "annotation_list_by_token", {"token": token})
    return [_mask_public_annotation(_record_to_annotation(record)) for record in records]


async def list_tags_by_share_token(
    session: AsyncSession,
    token: str,
) -> list[Tag]:
    records = await execute_query(session, "tag_list_by_token", {"token": token})
    return [_record_to_tag(record) for record in records]


async def get_shared_investigation(
    session: AsyncSession,
    token: str,
) -> SharedInvestigationResponse | None:
    investigation = await get_by_share_token(session, token)
    if investigation is None:
        return None

    annotations = await list_annotations_by_share_token(session, token)
    tags = await list_tags_by_share_token(session, token)
    return SharedInvestigationResponse(
        **investigation.model_dump(),
        annotations=annotations,
        tags=tags,
    )


async def import_investigation_bundle(
    session: AsyncSession,
    bundle: InvestigationExportBundle,
    user_id: str,
    title: str | None = None,
) -> InvestigationImportResponse:
    created = await create_investigation(
        session,
        title or bundle.investigation.title,
        bundle.investigation.description,
        user_id,
    )

    imported_entities = 0
    skipped_entity_ids: list[str] = []
    seen_entity_ids: set[str] = set()
    imported_entity_ids: set[str] = set()

    for entity_id in bundle.investigation.entity_ids:
        normalized = entity_id.strip()
        if not normalized or normalized in seen_entity_ids:
            continue
        seen_entity_ids.add(normalized)
        if await add_entity_to_investigation(session, created.id, normalized, user_id):
            imported_entities += 1
            imported_entity_ids.add(normalized)
        else:
            skipped_entity_ids.append(normalized)

    imported_annotations = 0
    for annotation in bundle.annotations:
        entity_id = annotation.entity_id.strip()
        if (
            not annotation.text.strip()
            or not entity_id
            or entity_id not in imported_entity_ids
        ):
            continue
        await create_annotation(
            session,
            created.id,
            entity_id,
            annotation.text,
            user_id,
        )
        imported_annotations += 1

    imported_tags = 0
    seen_tags: set[tuple[str, str]] = set()
    for tag in bundle.tags:
        name = tag.name.strip()
        color = tag.color.strip() or "#E07A2F"
        tag_key = (name.lower(), color.lower())
        if not name or tag_key in seen_tags:
            continue
        seen_tags.add(tag_key)
        await create_tag(session, created.id, name, color, user_id)
        imported_tags += 1

    investigation = await get_investigation(session, created.id, user_id)
    if investigation is None:
        msg = "Imported investigation could not be loaded"
        raise RuntimeError(msg)

    return InvestigationImportResponse(
        investigation=investigation,
        imported_entities=imported_entities,
        skipped_entity_ids=skipped_entity_ids,
        imported_annotations=imported_annotations,
        imported_tags=imported_tags,
    )


async def fork_shared_investigation(
    session: AsyncSession,
    token: str,
    user_id: str,
    title: str | None = None,
) -> InvestigationImportResponse | None:
    shared_investigation = await get_shared_investigation(session, token)
    if shared_investigation is None:
        return None

    default_title = title or f"{shared_investigation.title} (copy)"
    bundle = InvestigationExportBundle(
        investigation=InvestigationResponse(
            id=shared_investigation.id,
            title=shared_investigation.title,
            description=shared_investigation.description,
            created_at=shared_investigation.created_at,
            updated_at=shared_investigation.updated_at,
            entity_ids=shared_investigation.entity_ids,
            share_token=shared_investigation.share_token,
        ),
        annotations=shared_investigation.annotations,
        tags=shared_investigation.tags,
    )
    return await import_investigation_bundle(session, bundle, user_id, title=default_title)
