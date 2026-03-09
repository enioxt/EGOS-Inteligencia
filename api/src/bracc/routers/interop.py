"""Interop endpoints — NexusBridge cross-repo API.

Allows authenticated sibling repositories (egos-lab, carteira-livre)
to query the Neo4j graph securely via SERVICE_KEY authentication.

Auth: X-Service-Key header (not JWT — machine-to-machine only).
"""

import logging
import time
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from neo4j import AsyncSession

from bracc.config import settings
from bracc.dependencies import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/interop", tags=["interop"])


async def verify_service_key(
    x_service_key: Annotated[str | None, Header()] = None,
) -> str:
    """Validate the X-Service-Key header against configured INTEROP_SERVICE_KEY."""
    if not settings.interop_service_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Interop not configured (INTEROP_SERVICE_KEY not set)",
        )
    if not x_service_key or x_service_key != settings.interop_service_key:
        logger.warning("Interop auth failed — invalid or missing X-Service-Key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Service-Key",
        )
    return x_service_key


ServiceKey = Annotated[str, Depends(verify_service_key)]


async def _single(session: AsyncSession, cypher: str, params: dict | None = None) -> Any:
    """Run Cypher, return first value of first record (or None)."""
    result = await session.run(cypher, params or {})
    record = await result.single()
    return record[0] if record else None


async def _rows(session: AsyncSession, cypher: str, params: dict | None = None) -> list[dict]:
    """Run Cypher, return all records as dicts."""
    result = await session.run(cypher, params or {})
    return [dict(r) async for r in result]


@router.get("/health")
async def interop_health(
    _key: ServiceKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """Health check with Neo4j stats — for monitoring by sibling repos."""
    t0 = time.time()
    node_count = await _single(session, "MATCH (n) RETURN count(n)")
    rel_count = await _single(session, "MATCH ()-[r]->() RETURN count(r)")
    company_count = await _single(session, "MATCH (c:Company) RETURN count(c)")
    person_count = await _single(session, "MATCH (p:Person) RETURN count(p)")
    socio_de_count = await _single(session, "MATCH ()-[r:SOCIO_DE]->() RETURN count(r)")
    elapsed = time.time() - t0

    return {
        "status": "ok",
        "neo4j": {
            "nodes": node_count,
            "relationships": rel_count,
            "companies": company_count,
            "persons": person_count,
            "socio_de": socio_de_count,
        },
        "query_time_ms": round(elapsed * 1000, 1),
    }


@router.get("/entity/{cnpj}")
async def interop_entity(
    cnpj: str,
    _key: ServiceKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """Look up a Company by CNPJ and return its partners (SOCIO_DE)."""
    clean = cnpj.replace(".", "").replace("/", "").replace("-", "")
    if len(clean) != 14 or not clean.isdigit():
        raise HTTPException(status_code=400, detail="Invalid CNPJ format")

    rows = await _rows(
        session,
        """
        MATCH (c:Company {cnpj: $cnpj})
        RETURN c {.cnpj, .razao_social, .nome_fantasia, .uf, .municipio,
                   .situacao_cadastral, .cnae_fiscal, .porte_empresa} AS company
        LIMIT 1
        """,
        {"cnpj": clean},
    )
    company = rows[0]["company"] if rows else None
    if not company:
        return {"found": False, "cnpj": clean, "company": None, "partners": []}

    partner_rows = await _rows(
        session,
        """
        MATCH (p:Person)-[r:SOCIO_DE]->(c:Company {cnpj: $cnpj})
        RETURN p {.nome, .qualificacao, .data_entrada} AS partner
        LIMIT 50
        """,
        {"cnpj": clean},
    )
    partner_list = [r["partner"] for r in partner_rows]

    return {
        "found": True,
        "cnpj": clean,
        "company": company,
        "partners": partner_list,
    }


@router.get("/network/{cnpj}")
async def interop_network(
    cnpj: str,
    _key: ServiceKey,
    session: Annotated[AsyncSession, Depends(get_session)],
    hops: int = 1,
) -> dict:
    """Return the 1-hop (or N-hop) network around a CNPJ."""
    clean = cnpj.replace(".", "").replace("/", "").replace("-", "")
    if len(clean) != 14 or not clean.isdigit():
        raise HTTPException(status_code=400, detail="Invalid CNPJ format")
    if hops < 1 or hops > 3:
        raise HTTPException(status_code=400, detail="hops must be 1-3")

    query = f"""
    MATCH (c:Company {{cnpj: $cnpj}})
    OPTIONAL MATCH path = (c)-[*1..{hops}]-(connected)
    WHERE connected:Company OR connected:Person
    WITH c, connected, relationships(path) AS rels
    RETURN
        labels(connected)[0] AS type,
        connected.cnpj AS cnpj,
        connected.razao_social AS razao_social,
        connected.nome AS nome,
        [r IN rels | type(r)] AS rel_types
    LIMIT 100
    """
    results = await _rows(session, query, {"cnpj": clean})
    nodes = [
        {
            "type": r.get("type"),
            "cnpj": r.get("cnpj"),
            "razao_social": r.get("razao_social"),
            "nome": r.get("nome"),
            "rel_types": r.get("rel_types", []),
        }
        for r in results
    ]

    return {"cnpj": clean, "hops": hops, "network_size": len(nodes), "nodes": nodes}


@router.get("/sanctions/{cnpj}")
async def interop_sanctions(
    cnpj: str,
    _key: ServiceKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """Check if a CNPJ has any sanctions (CEIS, CNEP, barred NGOs)."""
    clean = cnpj.replace(".", "").replace("/", "").replace("-", "")
    if len(clean) != 14 or not clean.isdigit():
        raise HTTPException(status_code=400, detail="Invalid CNPJ format")

    sanction_rows = await _rows(
        session,
        """
        MATCH (c:Company {cnpj: $cnpj})-[r:SANCIONADA]->(s:Sanction)
        RETURN s {.tipo_sancao, .orgao_sancionador, .fundamentacao_legal,
                   .data_inicio, .data_fim} AS sanction
        LIMIT 20
        """,
        {"cnpj": clean},
    )
    sanction_list = [r["sanction"] for r in sanction_rows]

    barred_rows = await _rows(
        session,
        """
        MATCH (c:Company {cnpj: $cnpj})-[r:IMPEDIDA]->(b:BarredNGO)
        RETURN b {.motivo, .orgao, .data_referencia} AS barred
        LIMIT 10
        """,
        {"cnpj": clean},
    )
    barred_list = [r["barred"] for r in barred_rows]

    return {
        "cnpj": clean,
        "has_sanctions": len(sanction_list) > 0,
        "has_barred": len(barred_list) > 0,
        "sanctions": sanction_list,
        "barred": barred_list,
    }


@router.get("/pep/{query}")
async def interop_pep(
    query: str,
    _key: ServiceKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """Check if a name or CPF matches a PEP (Politically Exposed Person)."""
    clean = query.strip()
    if not clean or len(clean) < 3:
        raise HTTPException(status_code=400, detail="Query too short (min 3 chars)")

    is_cpf = clean.replace(".", "").replace("-", "").isdigit() and len(clean.replace(".", "").replace("-", "")) == 11

    if is_cpf:
        cpf_clean = clean.replace(".", "").replace("-", "")
        rows = await _rows(
            session,
            """
            MATCH (p:PEPRecord {cpf: $cpf})
            RETURN p {.nome, .cpf, .cargo, .orgao, .data_inicio, .data_fim} AS pep
            LIMIT 10
            """,
            {"cpf": cpf_clean},
        )
    else:
        rows = await _rows(
            session,
            """
            MATCH (p:PEPRecord)
            WHERE toLower(p.nome) CONTAINS toLower($name)
            RETURN p {.nome, .cpf, .cargo, .orgao, .data_inicio, .data_fim} AS pep
            LIMIT 20
            """,
            {"name": clean},
        )

    pep_list = [r["pep"] for r in rows]

    # Mask CPFs in response (LGPD)
    for pep in pep_list:
        if pep and pep.get("cpf"):
            cpf = str(pep["cpf"])
            if len(cpf) == 11:
                pep["cpf"] = f"***.***.{cpf[6:9]}-**"

    return {
        "query": clean,
        "is_pep": len(pep_list) > 0,
        "count": len(pep_list),
        "records": pep_list,
    }
