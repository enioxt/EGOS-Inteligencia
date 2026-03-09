"""Gazette Monitor — Eagle Eye bridge for EGOS Inteligência.

Periodically scans official gazettes for investigative patterns.
Feeds findings into the Activity Feed.
Can be triggered via API or cron.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

import httpx
from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/monitor/gazettes", tags=["gazette-monitor"])

QD_BASE = "https://api.queridodiario.ok.org.br"

# Investigative patterns — adapted from Eagle Eye
INVESTIGATIVE_PATTERNS = [
    {"query": "dispensa de licitação", "label": "Dispensa de Licitação", "risk": "high"},
    {"query": "inexigibilidade", "label": "Inexigibilidade", "risk": "high"},
    {"query": "aditivo contratual", "label": "Aditivo Contratual", "risk": "medium"},
    {"query": "emergência OR calamidade", "label": "Contratação Emergencial", "risk": "critical"},
    {"query": "sobrepreço OR superfaturamento", "label": "Indício de Sobrepreço", "risk": "critical"},
    {"query": "tomada de contas especial", "label": "Tomada de Contas", "risk": "high"},
    {"query": "multa OR penalidade OR suspensão", "label": "Sanção a Fornecedor", "risk": "medium"},
    {"query": "pregão deserto OR licitação fracassada", "label": "Licitação Fracassada", "risk": "medium"},
]

# Default monitored cities (configurable)
DEFAULT_CITIES = [
    ("3507506", "Botucatu", "SP"),
    ("3548500", "Santos", "SP"),
    ("3509502", "Campinas", "SP"),
    ("3518800", "Guarulhos", "SP"),
    ("3547809", "Santo André", "SP"),
    ("3543402", "Ribeirão Preto", "SP"),
    ("3549805", "São Bernardo do Campo", "SP"),
    ("3534401", "Osasco", "SP"),
    ("3530607", "Mogi das Cruzes", "SP"),
    ("3529401", "Mauá", "SP"),
]


async def _search_gazette(territory_id: str, query: str, days_back: int = 7) -> list[dict[str, Any]]:
    """Search gazettes for a specific pattern in a city."""
    since = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    params = {
        "territory_ids": territory_id,
        "querystring": query,
        "excerpt_size": 500,
        "number_of_excerpts": 2,
        "size": 5,
        "sort_by": "descending_date",
        "published_since": since,
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(f"{QD_BASE}/gazettes", params=params)
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for gz in data.get("gazettes", []):
                    results.append({
                        "date": gz.get("date", ""),
                        "city": gz.get("territory_name", ""),
                        "state": gz.get("state_code", ""),
                        "url": gz.get("url", ""),
                        "excerpts": [e[:500] for e in gz.get("excerpts", [])[:2]],
                    })
                return results
    except Exception as e:
        logger.warning("Gazette search failed for %s: %s", territory_id, e)
    return []


@router.get("/scan")
async def scan_gazettes(
    days: int = 7,
    city_id: str = "",
) -> dict[str, Any]:
    """Scan gazettes for investigative patterns. Returns alerts."""
    from bracc.routers.activity import log_activity

    cities = DEFAULT_CITIES
    if city_id:
        cities = [(city_id, city_id, "")]

    alerts: list[dict[str, Any]] = []
    total_scanned = 0

    for territory_id, city_name, uf in cities:
        for pattern in INVESTIGATIVE_PATTERNS:
            results = await _search_gazette(territory_id, pattern["query"], days)
            total_scanned += 1

            for r in results:
                alert = {
                    "city": r["city"] or city_name,
                    "state": r["state"] or uf,
                    "date": r["date"],
                    "pattern": pattern["label"],
                    "risk": pattern["risk"],
                    "url": r["url"],
                    "excerpt": r["excerpts"][0][:300] if r["excerpts"] else "",
                    "query": pattern["query"],
                }
                alerts.append(alert)

                # Log to activity feed
                log_activity(
                    activity_type="gazette_alert",
                    title=f"[{pattern['risk'].upper()}] {pattern['label']} — {r['city'] or city_name}",
                    description=r["excerpts"][0][:200] if r["excerpts"] else "",
                    source="Eagle Eye / Querido Diário",
                    result_count=1,
                )

    # Sort by risk
    risk_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    alerts.sort(key=lambda a: risk_order.get(a["risk"], 9))

    return {
        "scan_date": datetime.utcnow().isoformat() + "Z",
        "days_scanned": days,
        "cities_scanned": len(cities),
        "patterns_checked": len(INVESTIGATIVE_PATTERNS),
        "total_queries": total_scanned,
        "total_alerts": len(alerts),
        "alerts": alerts,
    }


@router.get("/patterns")
async def list_patterns() -> dict[str, Any]:
    """List all investigative patterns being monitored."""
    return {
        "count": len(INVESTIGATIVE_PATTERNS),
        "patterns": INVESTIGATIVE_PATTERNS,
        "cities": [{"id": c[0], "name": c[1], "uf": c[2]} for c in DEFAULT_CITIES],
    }
