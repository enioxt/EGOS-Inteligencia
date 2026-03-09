"""Pydantic models for the chat endpoint."""

from typing import Any

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    conversation_id: str = Field(default="", max_length=64)


class EntityCard(BaseModel):
    id: str
    type: str
    name: str
    properties: dict[str, Any] = {}
    connections: int = 0
    sources: list[str] = []


class EvidenceItem(BaseModel):
    tool: str
    source: str
    query: str
    result_count: int = 0
    timestamp: str = ""
    api_url: str = ""


class ChatResponse(BaseModel):
    reply: str
    entities: list[EntityCard] = []
    suggestions: list[str] = []
    evidence_chain: list[EvidenceItem] = []
    cost_usd: float = 0.0
