"""Chat endpoint — AI agent for EGOS Inteligência.

Full conversational agent with:
- LLM via OpenRouter (GPT-4o-mini — optimized for multi-tool calling)
- Neo4j graph search tools
- Conversation memory (in-memory per session, Redis planned)
- Contextual suggestions
- LGPD-compliant (no CPF exposure)
"""

import json
import logging
import re
import time
from collections import defaultdict
from typing import Annotated, Any

import httpx
from fastapi import APIRouter, Depends
from neo4j import AsyncSession
from starlette.requests import Request

from bracc.config import settings
from bracc.dependencies import get_session
from bracc.middleware.rate_limit import limiter
from bracc.routers.activity import log_activity
from bracc.services.cache import cache
from bracc.services.neo4j_service import execute_query, sanitize_props
from bracc.services.public_guard import (
    has_person_labels,
    sanitize_public_properties,
    should_hide_person_entities,
)
from bracc.services.transparency_tools import (
    tool_bnmp_mandados,
    tool_cnpj_info,
    tool_lista_suja,
    tool_oab_advogado,
    tool_opencnpj,
    tool_pncp_licitacoes,
    tool_procurados_lookup,
    tool_search_ceap,
    tool_search_contratos,
    tool_search_cpgf,
    tool_search_emendas,
    tool_search_gazettes,
    tool_search_licitacoes,
    tool_search_pep_city,
    tool_search_processos,
    tool_search_sancoes,
    tool_search_servidores,
    tool_search_transferencias,
    tool_search_viagens,
    tool_search_votacoes,
    tool_web_search,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["chat"])

_CNPJ_RE = re.compile(r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}")
_LUCENE_SPECIAL = re.compile(r'([+\-&|!(){}\[\]^"~*?:\\/])')

# --- In-memory conversation store (fallback when Redis unavailable) ---
_conversations: dict[str, list[dict[str, str]]] = defaultdict(list)
_conversation_ts: dict[str, float] = {}
_MAX_HISTORY = 20
_TTL_SECONDS = 1800

# --- Rate limit (in-memory fallback, Redis preferred) ---
_usage_counts: dict[str, int] = defaultdict(int)
_usage_day: dict[str, str] = {}

# Tier thresholds: msgs 1-10 = premium, 11-30 = free, 31+ = blocked (suggest BYOK)
_TIER_PREMIUM_LIMIT = 30
_TIER_FREE_LIMIT = 50

# Model tiers — all Gemini Flash for cost optimization (~$0.0003/query)
MODEL_PREMIUM = "google/gemini-2.0-flash-001"   # ~$0.0003/query, good tool-calling
MODEL_FREE = "google/gemini-2.0-flash-001"      # same model, no tier difference now
MODEL_FALLBACK = "google/gemini-2.0-flash-exp:free"  # free fallback when credits exhausted

_CREDIT_EXHAUSTED = False  # runtime flag set when 402/payment required detected

def _get_client_id(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _get_usage(client_id: str) -> int:
    """Get daily usage count from Redis (fallback: in-memory)."""
    today = time.strftime("%Y-%m-%d")
    redis = cache._client
    if redis and cache._available:
        try:
            key = f"egos:usage:{today}:{client_id}"
            val = await redis.get(key)
            return int(val) if val else 0
        except Exception:
            pass
    if _usage_day.get(client_id) != today:
        _usage_counts[client_id] = 0
        _usage_day[client_id] = today
    return _usage_counts[client_id]


async def _increment_usage(client_id: str) -> int:
    """Increment daily usage in Redis (fallback: in-memory). Returns new count."""
    today = time.strftime("%Y-%m-%d")
    redis = cache._client
    if redis and cache._available:
        try:
            key = f"egos:usage:{today}:{client_id}"
            new_val = await redis.incr(key)
            if new_val == 1:
                await redis.expire(key, 86400)
            return int(new_val)
        except Exception:
            pass
    if _usage_day.get(client_id) != today:
        _usage_counts[client_id] = 0
        _usage_day[client_id] = today
    _usage_counts[client_id] += 1
    return _usage_counts[client_id]


async def _select_model(client_id: str, byok_key: str = "") -> tuple[str, str, str]:
    """Select model based on usage tier or BYOK. Returns (model, api_key, tier_label)."""
    if byok_key:
        return MODEL_PREMIUM, byok_key, "byok"
    usage = await _get_usage(client_id)
    if usage < _TIER_PREMIUM_LIMIT:
        remaining = _TIER_PREMIUM_LIMIT - usage
        return MODEL_PREMIUM, settings.openrouter_api_key, f"premium ({remaining} restantes)"
    elif usage < _TIER_FREE_LIMIT:
        remaining = _TIER_FREE_LIMIT - usage
        return MODEL_FREE, settings.openrouter_api_key, f"gratuito ({remaining} restantes)"
    else:
        return MODEL_FREE, settings.openrouter_api_key, "limite_atingido"


def _get_conversation(client_id: str) -> list[dict[str, str]]:
    now = time.time()
    if client_id in _conversation_ts and (now - _conversation_ts[client_id]) > _TTL_SECONDS:
        _conversations[client_id] = []
    _conversation_ts[client_id] = now
    return _conversations[client_id]


def _trim_conversation(history: list[dict[str, str]]) -> None:
    while len(history) > _MAX_HISTORY:
        history.pop(0)


# --- Models (extracted to chat_models.py) ---
from bracc.routers.chat_models import ChatMessage, ChatResponse, EntityCard, EvidenceItem

# --- Neo4j tool functions ---

def _build_search_query(raw: str) -> str:
    raw = raw.strip()
    if any(c in raw for c in ['"', "*", "~", "AND", "OR"]):
        return raw
    escaped = _LUCENE_SPECIAL.sub(r"\\\1", raw)
    terms = escaped.split()
    parts: list[str] = []
    for term in terms:
        if len(term) >= 2:
            parts.append(f"{term}*")
            parts.append(f"{term}~0.8")
        else:
            parts.append(term)
    return " ".join(parts)


def _extract_name(node: Any, labels: list[str]) -> str:
    props = dict(node)
    etype = labels[0].lower() if labels else ""
    if etype == "company":
        return str(props.get("razao_social", props.get("name", props.get("nome_fantasia", ""))))
    if etype in ("contract", "amendment", "convenio"):
        return str(props.get("object", props.get("function", props.get("name", ""))))
    if etype == "embargo":
        return str(props.get("infraction", props.get("name", "")))
    if etype == "publicoffice":
        return str(props.get("org", props.get("name", "")))
    return str(props.get("name", ""))


def _format_type_pt(etype: str) -> str:
    labels = {
        "company": "Empresa", "person": "Pessoa", "contract": "Contrato",
        "sanction": "Sanção", "publicoffice": "Cargo Público", "embargo": "Embargo",
        "convenio": "Convênio", "election": "Eleição", "finance": "Financeiro",
        "partner": "Sócio",
    }
    return labels.get(etype, etype.capitalize())


async def _tool_search(session: AsyncSession, query: str, entity_type: str | None = None, limit: int = 8) -> list[EntityCard]:
    cnpj_match = _CNPJ_RE.search(query)
    if cnpj_match:
        cnpj_clean = re.sub(r"[.\-/]", "", cnpj_match.group())
        search_query = f'"{cnpj_clean}"'
    else:
        search_query = _build_search_query(query)

    records = await execute_query(
        session, "search",
        {"query": search_query, "entity_type": entity_type, "skip": 0, "limit": limit},
    )

    entities: list[EntityCard] = []
    for record in records:
        node = record["node"]
        props = dict(node)
        labels = record["node_labels"]

        if should_hide_person_entities() and has_person_labels(labels):
            continue

        source_val = props.pop("source", None)
        sources: list[str] = []
        if isinstance(source_val, str):
            sources = [source_val]
        elif isinstance(source_val, list):
            sources = [str(s) for s in source_val]

        etype = labels[0].lower() if labels else "unknown"
        clean_props = sanitize_public_properties(sanitize_props(props))

        entities.append(EntityCard(
            id=record["node_id"],
            type=etype,
            name=_extract_name(node, labels),
            properties=clean_props,
            connections=0,
            sources=sources,
        ))
    return entities


async def _tool_stats(session: AsyncSession) -> dict[str, Any]:
    try:
        records = await execute_query(session, "stats", {})
        if records:
            return dict(records[0])
    except Exception as e:
        logger.error("_tool_stats failed: %s", e)
    return {"error": "Não foi possível obter estatísticas"}


_CYPHER_ALLOWED_KEYWORDS = {
    "MATCH", "OPTIONAL", "RETURN", "WITH", "WHERE", "UNWIND", "ORDER", "BY",
    "LIMIT", "SKIP", "AS", "DISTINCT", "AND", "OR", "NOT", "IN", "IS", "NULL",
    "TRUE", "FALSE", "CONTAINS", "STARTS", "ENDS", "EXISTS", "CASE", "WHEN",
    "THEN", "ELSE", "END", "ASC", "DESC", "ASCENDING", "DESCENDING", "XOR",
    "COUNT", "SUM", "AVG", "MIN", "MAX", "COLLECT", "SIZE", "LENGTH", "KEYS",
    "LABELS", "TYPE", "ID", "COALESCE", "HEAD", "LAST", "TAIL", "RANGE",
    "TOSTRING", "TOINTEGER", "TOFLOAT", "TOBOOLEAN", "ELEMENTID",
}

_CYPHER_BLOCKED_PATTERNS = [
    "CREATE", "DELETE", "MERGE", "SET ", "REMOVE", "DROP", "DETACH",
    "CALL ", "CALL{", "LOAD CSV", "FOREACH", "USING PERIODIC",
    "CREATE INDEX", "CREATE CONSTRAINT", "GRANT", "REVOKE", "DENY",
]


async def _tool_cypher(session: AsyncSession, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Execute a safe read-only Cypher query. Whitelist-based: only MATCH/RETURN/WITH/UNWIND allowed."""
    q = query.strip().upper()
    for pattern in _CYPHER_BLOCKED_PATTERNS:
        if pattern in q:
            return [{"error": f"Query blocked: contains '{pattern.strip()}'. Only read-only queries allowed."}]
    tokens = re.findall(r'[A-Z_]+', q)
    for token in tokens:
        if len(token) >= 3 and token not in _CYPHER_ALLOWED_KEYWORDS and not token.startswith("$"):
            if token in {"CREATE", "DELETE", "MERGE", "REMOVE", "DROP", "DETACH", "CALL", "LOAD", "FOREACH", "GRANT", "REVOKE", "DENY"}:
                return [{"error": f"Query blocked: '{token}' is not allowed. Only read-only queries."}]
    try:
        result = await session.run(query, params or {})
        rows = []
        async for record in result:
            rows.append({k: _serialize_neo4j(record[k]) for k in record.keys()})
            if len(rows) >= 50:
                break
        return rows if rows else [{"message": "Query retornou 0 resultados"}]
    except Exception as e:
        logger.warning("Cypher query failed: %s — query: %s", e, query[:200])
        return [{"error": str(e)[:300]}]


def _serialize_neo4j(val: Any) -> Any:
    """Convert Neo4j types to JSON-serializable values."""
    if val is None:
        return None
    if isinstance(val, (str, int, float, bool)):
        return val
    if isinstance(val, list):
        return [_serialize_neo4j(v) for v in val]
    if isinstance(val, dict):
        return {k: _serialize_neo4j(v) for k, v in val.items()}
    if hasattr(val, 'items'):
        return {k: _serialize_neo4j(v) for k, v in val.items()}
    if hasattr(val, '__iter__'):
        return [_serialize_neo4j(v) for v in val]
    return str(val)


async def _tool_data_summary(session: AsyncSession) -> dict[str, Any]:
    """Dynamic data summary — replaces hardcoded stats in system prompt."""
    summary: dict[str, Any] = {"tools_count": len(TOOLS)}
    try:
        stats = await _tool_stats(session)
        if "error" not in stats:
            summary["total_nodes"] = stats.get("total_nodes", 0)
            summary["total_relationships"] = stats.get("total_relationships", 0)
            summary["data_sources"] = stats.get("data_sources", 0)
            summary["implemented_sources"] = stats.get("implemented_sources", 0)
            summary["loaded_sources"] = stats.get("loaded_sources", 0)
            summary["top_types"] = {
                k: v for k, v in stats.items()
                if k.endswith("_count") and isinstance(v, int) and v > 0 and k != "ingestion_run_count"
            }
    except Exception as e:
        summary["error"] = str(e)[:200]
    return summary


async def _tool_find_path(
    session: AsyncSession,
    entity_a_name: str,
    entity_b_name: str,
    max_depth: int = 4,
) -> dict[str, Any]:
    """Find shortest connection path between two entities (multi-hop traversal).

    Searches up to max_depth hops. Returns the path with relationship types,
    node names, and hop count. Cost is low for sparse graphs (<100K rels).
    """
    max_depth = min(max_depth, 6)  # Hard cap at 6 hops for safety
    try:
        # First, find both entities by name (fuzzy)
        find_cypher = """
        CALL db.index.fulltext.queryNodes('entity_search', $query)
        YIELD node, score
        WHERE score > 0.5
        RETURN elementId(node) AS id, labels(node) AS labels,
               coalesce(node.razao_social, node.name, node.nome_fantasia, '') AS name,
               score
        ORDER BY score DESC LIMIT 3
        """
        result_a = await session.run(find_cypher, {"query": entity_a_name})
        entities_a = [dict(r) async for r in result_a]

        result_b = await session.run(find_cypher, {"query": entity_b_name})
        entities_b = [dict(r) async for r in result_b]

        if not entities_a:
            return {"error": f"Entidade A não encontrada: {entity_a_name}", "entities_found": []}
        if not entities_b:
            return {"error": f"Entidade B não encontrada: {entity_b_name}", "entities_found": []}

        # Try shortest path between best matches
        # Note: Neo4j shortestPath doesn't support parameterized depth,
        # so we interpolate the validated integer directly into the query.
        path_cypher = f"""
        MATCH (a) WHERE elementId(a) = $id_a
        MATCH (b) WHERE elementId(b) = $id_b
        MATCH path = shortestPath((a)-[*1..{max_depth}]-(b))
        WITH path, length(path) AS hops
        RETURN
          [n IN nodes(path) |
            {{id: elementId(n), labels: labels(n),
             name: coalesce(n.razao_social, n.name, n.nome_fantasia, n.cpf, '')}}
          ] AS nodes,
          [r IN relationships(path) |
            {{type: type(r), from_id: elementId(startNode(r)), to_id: elementId(endNode(r))}}
          ] AS relationships,
          hops
        LIMIT 3
        """
        best_paths = []
        for ea in entities_a[:2]:
            for eb in entities_b[:2]:
                if ea["id"] == eb["id"]:
                    continue
                result = await session.run(
                    path_cypher,
                    {"id_a": ea["id"], "id_b": eb["id"]},
                )
                async for record in result:
                    best_paths.append({
                        "entity_a": ea["name"],
                        "entity_b": eb["name"],
                        "hops": record["hops"],
                        "nodes": record["nodes"],
                        "relationships": record["relationships"],
                    })

        if not best_paths:
            return {
                "connection_found": False,
                "message": f"Nenhuma conexão encontrada entre '{entity_a_name}' e '{entity_b_name}' em até {max_depth} graus.",
                "entity_a_candidates": [{"name": e["name"], "type": e["labels"][0]} for e in entities_a[:3]],
                "entity_b_candidates": [{"name": e["name"], "type": e["labels"][0]} for e in entities_b[:3]],
                "suggestion": "Tente aumentar max_depth ou verificar se os relacionamentos SOCIO_DE/DOOU estão carregados.",
            }

        # Sort by hops (shortest first)
        best_paths.sort(key=lambda p: p["hops"])
        return {
            "connection_found": True,
            "paths": best_paths[:3],
            "total_paths_found": len(best_paths),
            "min_hops": best_paths[0]["hops"] if best_paths else 0,
        }

    except Exception as e:
        logger.warning("Path finder failed: %s", e)
        return {"error": str(e), "suggestion": "Verifique se APOC está instalado e os índices existem."}


async def _tool_connections(session: AsyncSession, entity_id: str) -> list[dict[str, str]]:
    try:
        cypher = """
        MATCH (n)-[r]-(m)
        WHERE elementId(n) = $entity_id
        RETURN type(r) AS rel_type, labels(m) AS labels, 
               coalesce(m.razao_social, m.name, m.nome_fantasia, '') AS name
        LIMIT 15
        """
        result = await session.run(cypher, {"entity_id": entity_id})
        connections = []
        async for record in result:
            connections.append({
                "relationship": record["rel_type"],
                "type": record["labels"][0] if record["labels"] else "Unknown",
                "name": record["name"],
            })
        return connections
    except Exception as e:
        logger.warning("Connection lookup failed: %s", e)
        return []


# --- Tool definitions + System prompt (extracted to separate modules) ---
from bracc.routers.chat_prompt import SYSTEM_PROMPT
from bracc.routers.chat_tools import TOOLS


async def _call_openrouter(
    messages: list[dict[str, Any]],
    session: AsyncSession,
    model: str = "",
    api_key: str = "",
) -> tuple[str, list[EntityCard], list[dict[str, Any]], float]:
    """Call OpenRouter with tool-calling loop. Returns (reply_text, entities, evidence, cost)."""

    all_entities: list[EntityCard] = []
    evidence_chain: list[dict[str, Any]] = []
    total_cost: float = 0.0

    effective_key = api_key or settings.openrouter_api_key
    effective_model = model or settings.ai_model

    if not effective_key:
        text, ents = await _fallback_search(messages[-1].get("content", ""), session)
        return text, ents, [], 0.0

    headers = {
        "Authorization": f"Bearer {effective_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://inteligencia.egos.ia.br",
        "X-Title": "EGOS Inteligencia",
    }

    payload = {
        "model": effective_model,
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto",
        "max_tokens": 2000,
        "temperature": 0.3,
    }

    max_rounds = 8
    async with httpx.AsyncClient(timeout=45.0) as client:
        for _ in range(max_rounds):
            try:
                resp = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code in (402, 429):
                    global _CREDIT_EXHAUSTED
                    _CREDIT_EXHAUSTED = True
                    logger.warning("OpenRouter credits exhausted (HTTP %s). Switching to free model.", e.response.status_code)
                    # Retry with free fallback model
                    payload["model"] = MODEL_FALLBACK
                    headers["Authorization"] = f"Bearer {effective_key}"
                    try:
                        resp = await client.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers=headers,
                            json=payload,
                        )
                        resp.raise_for_status()
                        data = resp.json()
                    except Exception as e2:
                        logger.error("Fallback model also failed: %s", e2)
                        return (
                            "⚠️ **Créditos de IA esgotados.** Este projeto é 100% open-source e autofinanciado.\n\n"
                            "A busca direta no grafo ainda funciona — digite um CNPJ ou nome de empresa.\n\n"
                            "Se quiser ajudar a manter o chatbot ativo, qualquer contribuição ajuda:\n"
                            "- 🌟 [GitHub Star](https://github.com/enioxt/EGOS-Inteligencia)\n"
                            "- 💬 [Telegram](https://t.me/EthikIntelligence)",
                            [], [], 0.0,
                        )
                else:
                    logger.error("OpenRouter call failed: %s", e)
                    text, ents = await _fallback_search(messages[-1].get("content", ""), session)
                    return text, ents, [], 0.0
            except Exception as e:
                logger.error("OpenRouter call failed: %s", e)
                text, ents = await _fallback_search(messages[-1].get("content", ""), session)
                return text, ents, [], 0.0

            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})

            # Track token cost (~$0.15/1M input, $0.60/1M output for GPT-4o-mini)
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_cost += (prompt_tokens * 0.00000015) + (completion_tokens * 0.0000006)

            tool_calls = message.get("tool_calls")
            if not tool_calls:
                # Final text response
                return message.get("content", "Desculpe, não consegui processar sua pergunta."), all_entities, evidence_chain, total_cost

            # Process tool calls
            messages.append(message)
            for tc in tool_calls:
                fn_name = tc["function"]["name"]
                try:
                    fn_args = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    fn_args = {}

                result: Any = None
                if fn_name == "search_entities":
                    entities = await _tool_search(
                        session,
                        fn_args.get("query", ""),
                        fn_args.get("entity_type"),
                        min(fn_args.get("limit", 8), 20),
                    )
                    all_entities.extend(entities)
                    result = [{"id": e.id, "type": e.type, "name": e.name, "sources": e.sources, "properties": {k: v for k, v in list(e.properties.items())[:5]}} for e in entities]
                elif fn_name == "get_graph_stats":
                    result = await _tool_stats(session)
                elif fn_name == "get_entity_connections":
                    result = await _tool_connections(session, fn_args.get("entity_id", ""))
                elif fn_name == "find_connection_path":
                    result = await _tool_find_path(
                        session,
                        fn_args.get("entity_a", ""),
                        fn_args.get("entity_b", ""),
                        min(fn_args.get("max_depth", 4), 6),
                    )
                elif fn_name == "web_search":
                    result = await tool_web_search(
                        fn_args.get("query", ""),
                        min(fn_args.get("max_results", 5), 10),
                    )
                elif fn_name == "search_emendas":
                    result = await tool_search_emendas(
                        fn_args.get("municipio", ""),
                        fn_args.get("uf", ""),
                        fn_args.get("ano", 2024),
                    )
                elif fn_name == "search_transferencias":
                    result = await tool_search_transferencias(
                        fn_args.get("municipio", ""),
                        fn_args.get("uf", ""),
                        fn_args.get("ano", 2024),
                    )
                elif fn_name == "search_ceap":
                    result = await tool_search_ceap(
                        fn_args.get("parlamentar", ""),
                        fn_args.get("uf", ""),
                        fn_args.get("ano", 2024),
                    )
                elif fn_name == "search_pep_city":
                    result = await tool_search_pep_city(
                        fn_args.get("cidade", ""),
                        fn_args.get("uf", ""),
                    )
                elif fn_name == "search_gazettes":
                    result = await tool_search_gazettes(
                        fn_args.get("municipio", ""),
                        fn_args.get("query", ""),
                        min(fn_args.get("max_results", 5), 10),
                    )
                elif fn_name == "cnpj_info":
                    result = await tool_cnpj_info(fn_args.get("cnpj", ""))
                elif fn_name == "search_votacoes":
                    result = await tool_search_votacoes(
                        fn_args.get("parlamentar", ""),
                        fn_args.get("proposicao", ""),
                        fn_args.get("ano", 2024),
                    )
                elif fn_name == "search_servidores":
                    result = await tool_search_servidores(
                        fn_args.get("nome", ""),
                        fn_args.get("cpf", ""),
                        fn_args.get("orgao", ""),
                    )
                elif fn_name == "search_licitacoes":
                    result = await tool_search_licitacoes(
                        fn_args.get("orgao", ""),
                        fn_args.get("uf", ""),
                        fn_args.get("modalidade", ""),
                        fn_args.get("ano", 2024),
                    )
                elif fn_name == "search_cpgf":
                    result = await tool_search_cpgf(
                        fn_args.get("nome", ""),
                        fn_args.get("orgao", ""),
                        fn_args.get("mes", 0),
                        fn_args.get("ano", 2024),
                    )
                elif fn_name == "search_viagens":
                    result = await tool_search_viagens(
                        fn_args.get("nome", ""),
                        fn_args.get("orgao", ""),
                        fn_args.get("ano", 2024),
                    )
                elif fn_name == "search_contratos":
                    result = await tool_search_contratos(
                        fn_args.get("orgao", ""),
                        fn_args.get("fornecedor", ""),
                        fn_args.get("ano", 2024),
                    )
                elif fn_name == "search_sancoes":
                    result = await tool_search_sancoes(
                        fn_args.get("cnpj", ""),
                        fn_args.get("nome", ""),
                    )
                elif fn_name == "search_processos":
                    result = await tool_search_processos(
                        fn_args.get("numero_processo", ""),
                        fn_args.get("nome_parte", ""),
                        fn_args.get("tribunal", "TJSP"),
                        fn_args.get("classe", ""),
                    )
                elif fn_name == "bnmp_mandados":
                    result = await tool_bnmp_mandados(fn_args.get("nome", ""))
                elif fn_name == "procurados_lookup":
                    result = await tool_procurados_lookup(fn_args.get("nome", ""))
                elif fn_name == "lista_suja_lookup":
                    result = await tool_lista_suja(
                        fn_args.get("nome", ""),
                        fn_args.get("uf", ""),
                    )
                elif fn_name == "pncp_licitacoes":
                    result = await tool_pncp_licitacoes(
                        fn_args.get("cnpj_orgao", ""),
                        fn_args.get("uf", ""),
                        fn_args.get("data_inicio", "20240101"),
                        fn_args.get("data_fim", "20241231"),
                    )
                elif fn_name == "oab_advogado":
                    result = await tool_oab_advogado(
                        fn_args.get("nome", ""),
                        fn_args.get("numero_oab", ""),
                        fn_args.get("seccional", ""),
                    )
                elif fn_name == "opencnpj":
                    result = await tool_opencnpj(fn_args.get("cnpj", ""))
                elif fn_name == "cypher_query":
                    result = await _tool_cypher(session, fn_args.get("query", ""), fn_args.get("params"))
                elif fn_name == "data_summary":
                    result = await _tool_data_summary(session)
                else:
                    result = {"error": f"Tool {fn_name} not found"}

                # Track evidence chain
                source_info = {
                    "search_entities": ("Neo4j Graph", "neo4j://localhost:7687"),
                    "get_graph_stats": ("Neo4j Graph", "neo4j://localhost:7687"),
                    "get_entity_connections": ("Neo4j Graph", "neo4j://localhost:7687"),
                    "find_connection_path": ("Neo4j Graph — Path Finder", "neo4j://localhost:7687"),
                    "web_search": ("Brave Search / DuckDuckGo", "https://api.search.brave.com/"),
                    "search_emendas": ("Portal da Transparência — Emendas", "api.portaldatransparencia.gov.br"),
                    "search_transferencias": ("Portal da Transparência — Transferências", "api.portaldatransparencia.gov.br"),
                    "search_ceap": ("Câmara dos Deputados — CEAP", "dadosabertos.camara.leg.br"),
                    "search_pep_city": ("Câmara dos Deputados — PEP", "dadosabertos.camara.leg.br"),
                    "search_gazettes": ("Querido Diário (OKBR)", "queridodiario.ok.org.br"),
                    "cnpj_info": ("BrasilAPI — Receita Federal", "brasilapi.com.br"),
                    "search_votacoes": ("Câmara dos Deputados — Votações", "dadosabertos.camara.leg.br"),
                    "search_servidores": ("Portal da Transparência — Servidores", "api.portaldatransparencia.gov.br"),
                    "search_licitacoes": ("Portal da Transparência — Licitações", "api.portaldatransparencia.gov.br"),
                    "search_cpgf": ("Portal da Transparência — CPGF", "api.portaldatransparencia.gov.br"),
                    "search_viagens": ("Portal da Transparência — Viagens", "api.portaldatransparencia.gov.br"),
                    "search_contratos": ("Portal da Transparência — Contratos", "api.portaldatransparencia.gov.br"),
                    "search_sancoes": ("Portal da Transparência — CEIS/CNEP", "api.portaldatransparencia.gov.br"),
                    "search_processos": ("DataJud — CNJ", "api-publica.datajud.cnj.jus.br"),
                    "bnmp_mandados": ("BNMP — Mandados de Prisão (CNJ)", "portalbnmp.cnj.jus.br"),
                    "procurados_lookup": ("Polícia Federal — Procurados", "www.gov.br/pf"),
                    "lista_suja_lookup": ("MTE — Lista Suja Trabalho Escravo", "www.gov.br/trabalho-e-emprego"),
                    "pncp_licitacoes": ("PNCP — Licitações Nacionais", "pncp.gov.br"),
                    "oab_advogado": ("OAB — Cadastro de Advogados", "cna.oab.org.br"),
                    "opencnpj": ("OpenCNPJ — Receita Federal", "opencnpj.org"),
                    "cypher_query": ("Neo4j Graph — Cypher Query", "neo4j://localhost:7687"),
                    "data_summary": ("Sistema EGOS Inteligência", "inteligencia.egos.ia.br"),
                }.get(fn_name, ("Desconhecido", ""))

                result_count = 0
                if isinstance(result, list):
                    result_count = len(result)
                elif isinstance(result, dict):
                    for k in ("total", "count", "emendas", "transferencias", "deputados", "sancoes", "processos", "resultados", "results"):
                        v = result.get(k)
                        if isinstance(v, int):
                            result_count = v
                            break
                        elif isinstance(v, list):
                            result_count = len(v)
                            break

                from datetime import datetime
                evidence_chain.append({
                    "tool": fn_name,
                    "source": source_info[0],
                    "query": json.dumps(fn_args, ensure_ascii=False)[:200],
                    "result_count": result_count,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "api_url": source_info[1],
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(result, ensure_ascii=False, default=str)[:8000],
                })

            payload["messages"] = messages

    return "Desculpe, atingi o limite de processamento. Tente uma pergunta mais específica.", all_entities, evidence_chain, total_cost


async def _fallback_search(user_msg: str, session: AsyncSession) -> tuple[str, list[EntityCard]]:
    """Fallback when no OpenRouter key: direct Neo4j search."""
    cnpj_match = _CNPJ_RE.search(user_msg)
    if cnpj_match:
        term = cnpj_match.group()
    else:
        cleaned = re.sub(
            r"\b(quem|qual|quais|onde|como|sobre|me|fale|busque|pesquise|procure|"
            r"encontre|mostre|o que|é|são|do|da|de|dos|das|no|na|nos|nas|"
            r"um|uma|uns|umas|para|por|com|em|a|e|ou|os|as|ao|à|"
            r"tem|ter|foi|ser|está|estão|pode|podem)\b",
            "", user_msg.lower(),
        )
        term = re.sub(r"\s+", " ", cleaned).strip()

    if len(term) < 2:
        return (
            "Olá! Sou o agente de inteligência do **EGOS**.\n\nDigite um CNPJ, nome de empresa, ou pergunte sobre dados públicos brasileiros.",
            [],
        )

    entities = await _tool_search(session, term)

    if not entities:
        return f'Não encontrei resultados para **"{term}"**.\n\nTente verificar a ortografia ou usar o CNPJ completo.', []
    elif len(entities) == 1:
        e = entities[0]
        reply = f"Encontrei **{_format_type_pt(e.type)}**: **{e.name}**"
        if e.sources:
            reply += f"\nFonte: {', '.join(e.sources)}"
        return reply, entities
    else:
        reply = f"Encontrei **{len(entities)} resultados** para \"{term}\":\n\n"
        for i, e in enumerate(entities, 1):
            reply += f"{i}. **{e.name}** ({_format_type_pt(e.type)})\n"
        return reply, entities


def _generate_suggestions(reply: str, entities: list[EntityCard], user_msg: str) -> list[str]:
    """Generate contextual investigative follow-up suggestions."""
    suggestions: list[str] = []
    msg_lower = user_msg.lower()
    reply_lower = reply.lower()

    # City-related suggestions
    _BR_CITIES = ["uberlandia", "sao paulo", "rio de janeiro", "belo horizonte", "brasilia",
                  "curitiba", "salvador", "fortaleza", "recife", "porto alegre", "goiania",
                  "manaus", "campinas", "patos de minas", "uberaba", "juiz de fora"]
    detected_city = None
    for city in _BR_CITIES:
        if city in msg_lower or city in reply_lower:
            detected_city = city.title()
            break

    if detected_city:
        suggestions.append(f"Emendas para {detected_city}")
        suggestions.append(f"Deputados de {detected_city}")
        suggestions.append(f"Transferencias federais {detected_city}")

    # Entity-based suggestions
    if entities:
        first = entities[0]
        if first.type == "company":
            suggestions.append(f"Conexoes de {first.name[:25]}")
            suggestions.append(f"Sancoes contra {first.name[:25]}")
        elif first.type == "person":
            suggestions.append(f"Gastos CEAP de {first.name[:25]}")
        elif first.type == "sanction":
            suggestions.append("Buscar empresa sancionada no grafo")

    # CEAP/transparency suggestions
    if "ceap" in reply_lower or "deputad" in reply_lower:
        suggestions.append("Fornecedores desse deputado")
        suggestions.append("Gastos com passagens aereas")

    # If no context-specific suggestions, use investigative defaults
    if not suggestions:
        import random
        _INVESTIGATION_SUGGESTIONS = [
            "Digite o nome da sua cidade",
            "Gastos CEAP deputados SP",
            "Emendas parlamentares 2024",
            "Buscar empresa por CNPJ",
            "Votacoes recentes na Camara",
            "Recuperacao judicial empresas",
            "Investigacoes Ministerio Publico",
            "Diario oficial licitacoes",
            "Supersalarios servidores publicos",
            "Fornecedores de politicos",
        ]
        suggestions = random.sample(_INVESTIGATION_SUGGESTIONS, min(4, len(_INVESTIGATION_SUGGESTIONS)))

    return suggestions[:4]


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("30/minute")
async def chat(
    request: Request,
    body: ChatMessage,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ChatResponse:
    """AI-powered conversational search for EGOS Inteligência."""

    client_id = _get_client_id(request)

    # Conversation persistence: use Redis if conversation_id provided
    conv_id = body.conversation_id.strip() if body.conversation_id else ""
    client_header = (request.headers.get("x-client-id") or "").strip()
    effective_client = client_header if client_header else client_id

    if conv_id:
        from bracc.routers.conversations import get_conversation_messages
        history = await get_conversation_messages(conv_id, effective_client)
    else:
        history = _get_conversation(client_id)

    # BYOK: user can pass own OpenRouter key via header
    byok_key = (request.headers.get("x-openrouter-key") or "").strip()

    # Select model based on usage tier or BYOK
    selected_model, selected_key, tier_label = await _select_model(client_id, byok_key)

    # Rate limit check — if limit reached, prepend warning
    tier_notice = ""
    if tier_label == "limite_atingido":
        tier_notice = "\n\n⚠️ **Limite diário atingido** (30 consultas). O agente continua funcionando com modelo gratuito, mas a qualidade pode ser menor.\n\n💡 **Traga sua própria chave!** Crie uma conta grátis em [openrouter.ai](https://openrouter.ai), insira créditos (~$5 dura meses) e cole sua chave nas configurações. Assim você usa os melhores modelos sem restrição."

    # Prompt injection soft check (logs but does not block)
    from bracc.middleware.input_sanitizer import check_injection
    injection_pattern = check_injection(body.message)
    if injection_pattern:
        log_activity("prompt_injection_detected", {"pattern": injection_pattern[:80], "client": client_id})

    # Build messages for LLM
    messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history (last N messages for context)
    for msg in history[-10:]:
        messages.append(msg)

    # Enrich vague queries with actionable hints for the LLM
    enriched_msg = body.message
    msg_lower = body.message.lower().strip()
    _QUERY_HINTS: list[tuple[list[str], str]] = [
        (["estatistic", "quantos dados", "quantas entidade", "o que voce sabe", "o que você sabe", "quais dados", "quais fontes", "resumo do sistema"],
         "Chame data_summary E cypher_query com 'MATCH (n) RETURN labels(n)[0] AS tipo, count(n) AS total ORDER BY total DESC LIMIT 15'. Mostre os números reais."),
        (["relatorio", "relatório", "report", "exemplos de investigacao"],
         "Liste os 4 relatórios publicados com links: SUPERAR, Manaus, RJ SP, Patense. Ofereça para investigar algo novo."),
        (["emendas parlamentar", "emendas 2024"],
         "Chame search_emendas para SP em 2024 E search_transferencias para SP em 2024. Mostre maiores valores."),
        (["supersalario", "supersalário", "maiores salario"],
         "Chame search_servidores sem filtro (mostra maiores salários) E cypher_query com 'MATCH (p:PEPRecord) RETURN p.name, p.source LIMIT 10'."),
        (["licitacoes suspeita", "licitações suspeita", "dispensa de licitacao"],
         "Chame search_licitacoes para SP 2024 E pncp_licitacoes para SP. Analise dispensas."),
        (["diario oficial", "diário oficial"],
         "Chame search_gazettes para a cidade mencionada (ou São Paulo) com query 'licitação'."),
        (["votacoes recentes", "votações recentes", "como votou"],
         "Chame search_votacoes para 2024. Mostre votações recentes com placar."),
        (["empresas sancionada", "lista suja", "ceis", "cnep"],
         "Chame cypher_query com 'MATCH (s:Sanction) RETURN s.name, s.source, s.value LIMIT 15' E search_sancoes."),
        (["o que voce pode", "o que você pode", "ajuda", "help", "como funciona", "o que faz"],
         "Chame data_summary. Depois explique: 26 ferramentas, acesso a Neo4j, Portal da Transparência, DataJud, BNMP, diários oficiais, CNPJ, mandados, sanções. Sugira investigações."),
    ]
    for triggers, hint in _QUERY_HINTS:
        if any(t in msg_lower for t in triggers):
            enriched_msg = f"{body.message}\n\n[SISTEMA: {hint}]"
            break

    messages.append({"role": "user", "content": enriched_msg})

    try:
        reply, entities, evidence, cost = await _call_openrouter(
            messages, session, model=selected_model, api_key=selected_key
        )
    except Exception as e:
        logger.error("Chat failed: %s", e)
        reply, entities = await _fallback_search(body.message, session)
        evidence, cost = [], 0.0

    # Increment usage AFTER successful call
    new_count = await _increment_usage(client_id)

    # Append tier notice to reply
    if tier_notice:
        reply += tier_notice
    elif new_count == _TIER_PREMIUM_LIMIT:
        reply += f"\n\n💡 Você usou suas {_TIER_PREMIUM_LIMIT} consultas premium do dia. Próximas consultas usarão o modelo gratuito (Gemini Flash). Para manter a qualidade, traga sua chave OpenRouter."
    elif new_count == _TIER_FREE_LIMIT:
        reply += "\n\n⚠️ Limite diário atingido. Crie uma conta grátis em [openrouter.ai](https://openrouter.ai) e insira sua chave para continuar sem limites."

    # Save to conversation memory
    if conv_id:
        from bracc.routers.conversations import save_conversation_messages
        await save_conversation_messages(
            conv_id, effective_client, body.message, reply, auto_title=True
        )
    else:
        history.append({"role": "user", "content": body.message})
        history.append({"role": "assistant", "content": reply})
        _trim_conversation(history)

    suggestions = _generate_suggestions(reply, entities, body.message)

    # Log activity with tier info
    log_activity(
        activity_type="chat",
        title=body.message[:80],
        description=f"{len(entities)} entities, {len(evidence)} sources, model={selected_model.split('/')[-1]}, tier={tier_label}",
        source="chatbot",
        result_count=len(entities),
        cost_usd=round(cost, 6),
        client_ip=client_id,
    )

    return ChatResponse(
        reply=reply,
        entities=entities,
        suggestions=suggestions,
        evidence_chain=[EvidenceItem(**e) for e in evidence],
        cost_usd=round(cost, 6),
    )
