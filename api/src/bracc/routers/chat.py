"""Chat endpoint — AI agent for EGOS Inteligência.

Full conversational agent with:
- LLM via OpenRouter (Gemini 2.0 Flash)
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
from pydantic import BaseModel, Field
from starlette.requests import Request

from bracc.config import settings
from bracc.dependencies import get_session
from bracc.middleware.rate_limit import limiter
from bracc.services.neo4j_service import execute_query, sanitize_props
from bracc.services.public_guard import (
    has_person_labels,
    sanitize_public_properties,
    should_hide_person_entities,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["chat"])

_CNPJ_RE = re.compile(r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}")
_LUCENE_SPECIAL = re.compile(r'([+\-&|!(){}\[\]^"~*?:\\/])')

# --- In-memory conversation store (keyed by IP, max 20 messages, 30min TTL) ---
_conversations: dict[str, list[dict[str, str]]] = defaultdict(list)
_conversation_ts: dict[str, float] = {}
_MAX_HISTORY = 20
_TTL_SECONDS = 1800


def _get_client_id(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _get_conversation(client_id: str) -> list[dict[str, str]]:
    now = time.time()
    if client_id in _conversation_ts and (now - _conversation_ts[client_id]) > _TTL_SECONDS:
        _conversations[client_id] = []
    _conversation_ts[client_id] = now
    return _conversations[client_id]


def _trim_conversation(history: list[dict[str, str]]) -> None:
    while len(history) > _MAX_HISTORY:
        history.pop(0)


# --- Models ---

class ChatMessage(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class EntityCard(BaseModel):
    id: str
    type: str
    name: str
    properties: dict[str, Any] = {}
    connections: int = 0
    sources: list[str] = []


class ChatResponse(BaseModel):
    reply: str
    entities: list[EntityCard] = []
    suggestions: list[str] = []


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
    except Exception:
        pass
    return {"error": "Não foi possível obter estatísticas"}


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


# --- Tool definitions for OpenRouter function calling ---

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_entities",
            "description": "Pesquisa entidades no grafo Neo4j por nome, CNPJ, ou termo. Retorna empresas, sanções, contratos, embargos, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Termo de busca: nome de empresa, CNPJ, ou palavra-chave"},
                    "entity_type": {"type": "string", "description": "Filtro opcional: company, sanction, contract, embargo, person, election, finance", "enum": ["company", "sanction", "contract", "embargo", "person", "election", "finance", "convenio", "publicoffice"]},
                    "limit": {"type": "integer", "description": "Máximo de resultados (1-20)", "default": 8},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_graph_stats",
            "description": "Retorna estatísticas gerais do grafo: total de nós, relacionamentos, contagem por tipo de entidade.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_entity_connections",
            "description": "Busca conexões/relacionamentos de uma entidade específica no grafo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "ID da entidade (elementId do Neo4j)"},
                },
                "required": ["entity_id"],
            },
        },
    },
]

SYSTEM_PROMPT = """Você é o agente de inteligência do EGOS Inteligência (inteligencia.egos.ia.br).

## Quem você é
- Assistente de pesquisa em dados públicos brasileiros
- Acesso ao grafo Neo4j com 317 mil+ entidades e 34 mil+ conexões
- Bases: CEIS, CNEP, OpenSanctions, PEP, CEAF, CPGF, TSE, BNDES, IBAMA, DATASUS, TransfereGov, RAIS, INEP
- Projeto 100% open-source, sem investidores, autofinanciado

## Regras
- Responda SEMPRE em português brasileiro
- Máximo 600 caracteres por resposta (seja conciso e direto)
- Use **negrito** para destacar nomes e números importantes
- NUNCA exponha CPF, dados pessoais sensíveis
- Padrões encontrados são SINAIS, nunca prova jurídica
- Sempre cite a fonte dos dados (CEIS, CNEP, TSE, etc.)
- Se não encontrar resultados, sugira variações de busca
- Use as ferramentas proativamente — não peça permissão, busque
- Quando o usuário mencionar uma empresa ou CNPJ, use search_entities automaticamente
- Sugira próximos passos úteis ao final

## Bases que AINDA NÃO temos (seja honesto)
- CNPJ/QSA completo (ETL em andamento — 53M empresas sendo carregadas)
- DataJud (processos judiciais)
- ICIJ Offshore Leaks
- ComprasNet/PNCP
- CVM (mercado financeiro)

## Disclaimer (inclua quando relevante)
Pesquisa pessoal com dados públicos. Padrões são sinais, não prova jurídica."""


async def _call_openrouter(
    messages: list[dict[str, Any]],
    session: AsyncSession,
) -> tuple[str, list[EntityCard]]:
    """Call OpenRouter with tool-calling loop. Returns (reply_text, entities)."""

    all_entities: list[EntityCard] = []

    if not settings.openrouter_api_key:
        # Fallback to direct search if no API key
        return await _fallback_search(messages[-1].get("content", ""), session)

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": f"https://{settings.cors_origins.split(',')[0].strip().replace('http://', '').replace('https://', '')}",
        "X-Title": "EGOS Inteligência",
    }

    payload = {
        "model": settings.ai_model,
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto",
        "max_tokens": 800,
        "temperature": 0.3,
    }

    max_rounds = 4
    async with httpx.AsyncClient(timeout=30.0) as client:
        for _ in range(max_rounds):
            try:
                resp = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                logger.error("OpenRouter call failed: %s", e)
                return await _fallback_search(messages[-1].get("content", ""), session)

            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})

            tool_calls = message.get("tool_calls")
            if not tool_calls:
                # Final text response
                return message.get("content", "Desculpe, não consegui processar sua pergunta."), all_entities

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
                else:
                    result = {"error": f"Tool {fn_name} not found"}

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(result, ensure_ascii=False, default=str)[:4000],
                })

            payload["messages"] = messages

    return "Desculpe, atingi o limite de processamento. Tente uma pergunta mais específica.", all_entities


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
    """Generate contextual follow-up suggestions."""
    suggestions: list[str] = []

    if entities:
        first = entities[0]
        if first.type == "company":
            suggestions.append(f"Sanções contra {first.name[:25]}")
            suggestions.append(f"Conexões de {first.name[:25]}")
        elif first.type == "sanction":
            suggestions.append("Buscar empresa sancionada")
        if len(entities) > 3:
            suggestions.append("Refinar busca")

    if not suggestions:
        suggestions = ["Buscar por CNPJ", "Ver estatísticas do grafo", "Sanções recentes"]

    if "estatístic" not in reply.lower():
        suggestions.append("Ver estatísticas")

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
    history = _get_conversation(client_id)

    # Build messages for LLM
    messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history (last N messages for context)
    for msg in history[-10:]:
        messages.append(msg)

    messages.append({"role": "user", "content": body.message})

    try:
        reply, entities = await _call_openrouter(messages, session)
    except Exception as e:
        logger.error("Chat failed: %s", e)
        reply, entities = await _fallback_search(body.message, session)

    # Save to conversation memory
    history.append({"role": "user", "content": body.message})
    history.append({"role": "assistant", "content": reply})
    _trim_conversation(history)

    suggestions = _generate_suggestions(reply, entities, body.message)

    return ChatResponse(
        reply=reply,
        entities=entities,
        suggestions=suggestions,
    )
