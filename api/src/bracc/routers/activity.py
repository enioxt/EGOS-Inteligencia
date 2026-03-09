"""Activity Feed — Mycelium-inspired event trail for EGOS Inteligência.

Cumulative counters persisted in Redis (survive container restarts).
Recent events kept in-memory deque (last 500) for timeline display.
"""
import logging
import time
from collections import deque
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

from bracc.services.cache import cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/activity", tags=["activity"])

# In-memory recent events (last 500) for timeline
_ACTIVITY_LOG: deque[dict[str, Any]] = deque(maxlen=500)

# Redis key prefix for persistent counters
_R = "egos:activity"


class ActivityItem(BaseModel):
    id: str
    type: str  # search, chat, report, entity_view, tool_call
    title: str
    description: str = ""
    source: str = ""
    result_count: int = 0
    cost_usd: float = 0.0
    timestamp: str = ""
    client_ip: str = ""


async def _redis_incr(key: str, amount: int = 1) -> None:
    """Increment a Redis counter (best-effort, no-op if unavailable)."""
    r = cache._client
    if not r or not cache._available:
        return
    try:
        await r.incrby(key, amount)
    except Exception:
        pass


async def _redis_incr_float(key: str, amount: float) -> None:
    r = cache._client
    if not r or not cache._available:
        return
    try:
        await r.incrbyfloat(key, amount)
    except Exception:
        pass


async def _redis_get_int(key: str) -> int:
    r = cache._client
    if not r or not cache._available:
        return 0
    try:
        val = await r.get(key)
        return int(val) if val else 0
    except Exception:
        return 0


async def _redis_get_float(key: str) -> float:
    r = cache._client
    if not r or not cache._available:
        return 0.0
    try:
        val = await r.get(key)
        return float(val) if val else 0.0
    except Exception:
        return 0.0


async def _redis_get_hash(key: str) -> dict[str, int]:
    r = cache._client
    if not r or not cache._available:
        return {}
    try:
        data = await r.hgetall(key)
        return {k: int(v) for k, v in data.items()} if data else {}
    except Exception:
        return {}


def log_activity(
    activity_type: str,
    title: str,
    description: str = "",
    source: str = "",
    result_count: int = 0,
    cost_usd: float = 0.0,
    client_ip: str = "",
    model: str = "",
) -> None:
    """Log an activity event to in-memory store + queue Redis persistence."""
    event = {
        "id": f"evt-{int(time.time() * 1000)}",
        "type": activity_type,
        "title": title,
        "description": description,
        "source": source,
        "result_count": result_count,
        "cost_usd": cost_usd,
        "model": model,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "client_ip": client_ip,
    }
    _ACTIVITY_LOG.appendleft(event)
    # Fire-and-forget Redis persistence (runs in background on next await)
    import asyncio
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_persist_counters(activity_type, source, result_count, cost_usd, client_ip, model))
    except RuntimeError:
        pass


async def _persist_counters(
    activity_type: str, source: str, result_count: int,
    cost_usd: float, client_ip: str, model: str,
) -> None:
    """Persist cumulative counters to Redis."""
    today = time.strftime("%Y-%m-%d")
    await _redis_incr(f"{_R}:total")
    await _redis_incr(f"{_R}:daily:{today}")
    if cost_usd > 0:
        await _redis_incr_float(f"{_R}:cost_usd", cost_usd)
    if result_count > 0:
        await _redis_incr(f"{_R}:results", result_count)

    # Hash counters for breakdowns
    r = cache._client
    if r and cache._available:
        try:
            await r.hincrby(f"{_R}:by_type", activity_type, 1)
            if source:
                await r.hincrby(f"{_R}:by_source", source, 1)
            if model:
                await r.hincrby(f"{_R}:by_model", model, 1)
            if client_ip and client_ip != "unknown":
                await r.sadd(f"{_R}:unique_ips", client_ip)
        except Exception as exc:
            logger.debug("Redis activity persist failed: %s", exc)


@router.get("/feed")
async def get_activity_feed(
    request: Request,
    limit: int = 50,
    type: str = "",
) -> dict[str, Any]:
    """Get recent activity feed + cumulative stats from Redis."""
    items = list(_ACTIVITY_LOG)
    if type:
        items = [i for i in items if i["type"] == type]
    items = items[:min(limit, 200)]

    # Cumulative stats from Redis (lifetime, not just in-memory)
    total_lifetime = await _redis_get_int(f"{_R}:total")
    total_cost = await _redis_get_float(f"{_R}:cost_usd")
    total_results = await _redis_get_int(f"{_R}:results")
    by_type = await _redis_get_hash(f"{_R}:by_type")
    by_source = await _redis_get_hash(f"{_R}:by_source")
    by_model = await _redis_get_hash(f"{_R}:by_model")

    # Unique users
    unique_users = 0
    r = cache._client
    if r and cache._available:
        try:
            unique_users = await r.scard(f"{_R}:unique_ips") or 0
        except Exception:
            pass

    # Fallback to in-memory if Redis empty
    if total_lifetime == 0:
        total_lifetime = len(_ACTIVITY_LOG)
        for item in _ACTIVITY_LOG:
            t = item.get("type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
            total_cost += item.get("cost_usd", 0.0)

    # Daily counts (last 7 days)
    daily: dict[str, int] = {}
    if r and cache._available:
        try:
            import datetime as dt
            for i in range(7):
                d = (dt.datetime.utcnow() - dt.timedelta(days=i)).strftime("%Y-%m-%d")
                val = await r.get(f"{_R}:daily:{d}")
                daily[d] = int(val) if val else 0
        except Exception:
            pass

    return {
        "items": items,
        "stats": {
            "total_events": total_lifetime,
            "session_events": len(_ACTIVITY_LOG),
            "by_type": by_type,
            "by_source": dict(sorted(by_source.items(), key=lambda x: x[1], reverse=True)[:15]),
            "by_model": by_model,
            "total_cost_usd": round(total_cost, 6),
            "total_results": total_results,
            "unique_users": unique_users,
            "avg_cost_per_query": round(total_cost / max(total_lifetime, 1), 6),
            "daily": daily,
        },
    }


@router.get("/stats")
async def get_activity_stats() -> dict[str, Any]:
    """Get aggregated activity statistics (cumulative)."""
    total = await _redis_get_int(f"{_R}:total")
    total_cost = await _redis_get_float(f"{_R}:cost_usd")
    total_results = await _redis_get_int(f"{_R}:results")
    by_type = await _redis_get_hash(f"{_R}:by_type")
    by_source = await _redis_get_hash(f"{_R}:by_source")
    by_model = await _redis_get_hash(f"{_R}:by_model")

    unique_users = 0
    r = cache._client
    if r and cache._available:
        try:
            unique_users = await r.scard(f"{_R}:unique_ips") or 0
        except Exception:
            pass

    if total == 0:
        total = len(_ACTIVITY_LOG)
        for item in _ACTIVITY_LOG:
            t = item.get("type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
            s = item.get("source", "unknown")
            by_source[s] = by_source.get(s, 0) + 1
            total_cost += item.get("cost_usd", 0.0)
            total_results += item.get("result_count", 0)

    return {
        "total_events": total,
        "by_type": by_type,
        "by_source": dict(sorted(by_source.items(), key=lambda x: x[1], reverse=True)[:15]),
        "by_model": by_model,
        "total_cost_usd": round(total_cost, 6),
        "total_results": total_results,
        "unique_users": unique_users,
        "avg_cost_per_query": round(total_cost / max(total, 1), 6),
    }
