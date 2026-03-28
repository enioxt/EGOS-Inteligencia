"""
EGOS Agent Registry API — serves agent definitions from egos kernel
GET /api/agents — list all kernel agents
GET /api/agents/{agent_id} — get specific agent
"""

import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/agents", tags=["agents"])

EGOS_REGISTRY_PATH = os.environ.get(
    "EGOS_AGENTS_REGISTRY",
    "/opt/bracc/egos/agents/registry/agents.json"
)

# Fallback inline registry (kernel 6 agents, 2026-03-28)
FALLBACK_REGISTRY = {
    "version": "1.0.0",
    "source": "fallback",
    "agents": [
        {"id": "dep-auditor", "name": "Dependency Auditor", "area": "architecture", "status": "active"},
        {"id": "archaeology-digger", "name": "Archaeology Digger", "area": "knowledge", "status": "active"},
        {"id": "chatbot-compliance-checker", "name": "Chatbot Compliance Checker", "area": "compliance", "status": "active"},
        {"id": "dead-code-detector", "name": "Dead Code Detector", "area": "architecture", "status": "active"},
        {"id": "capability-drift-checker", "name": "Capability Drift Checker", "area": "governance", "status": "active"},
        {"id": "context-tracker", "name": "Context Tracker", "area": "observability", "status": "active"},
    ]
}


def load_registry() -> dict:
    if os.path.exists(EGOS_REGISTRY_PATH):
        with open(EGOS_REGISTRY_PATH) as f:
            data = json.load(f)
            data["source"] = "live"
            return data
    return FALLBACK_REGISTRY


@router.get("")
def list_agents():
    registry = load_registry()
    return {
        "version": registry.get("version", "1.0.0"),
        "source": registry.get("source", "fallback"),
        "count": len(registry.get("agents", [])),
        "agents": registry.get("agents", []),
    }


@router.get("/{agent_id}")
def get_agent(agent_id: str):
    registry = load_registry()
    agents = registry.get("agents", [])
    agent = next((a for a in agents if a["id"] == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return agent
