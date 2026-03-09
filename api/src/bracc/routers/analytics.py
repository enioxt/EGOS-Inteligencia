import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


class PageViewEvent(BaseModel):
    page: str
    referrer: str = ""


class AnalyticsResponse(BaseModel):
    status: str = "ok"


async def _get_redis():
    """Get Redis client from cache singleton."""
    from bracc.services.cache import cache
    if cache._client:
        return cache._client
    return None


@router.post("/pageview", response_model=AnalyticsResponse)
async def track_pageview(request: Request, event: PageViewEvent) -> AnalyticsResponse:
    """Track a page view. Lightweight, no PII stored."""
    try:
        redis = await _get_redis()
        if redis:
            today = datetime.now(UTC).strftime("%Y-%m-%d")
            hour = datetime.now(UTC).strftime("%H")
            ip_hash = str(hash(request.client.host if request.client else "unknown"))[-8:]

            pipe = redis.pipeline()
            pipe.hincrby(f"analytics:pv:{today}", event.page, 1)
            pipe.hincrby(f"analytics:hourly:{today}", hour, 1)
            pipe.sadd(f"analytics:uv:{today}", ip_hash)
            pipe.expire(f"analytics:uv:{today}", 86400 * 7)
            pipe.expire(f"analytics:pv:{today}", 86400 * 30)
            pipe.expire(f"analytics:hourly:{today}", 86400 * 7)
            pipe.incr("analytics:total_pv")
            await pipe.execute()
    except Exception as e:
        logger.warning("Analytics tracking failed: %s", e)

    return AnalyticsResponse()


@router.get("/summary")
async def analytics_summary() -> dict[str, Any]:
    """Get analytics summary. No auth required (public stats)."""
    try:
        redis = await _get_redis()
        if not redis:
            return {"error": "Redis not available"}

        today = datetime.now(UTC).strftime("%Y-%m-%d")

        pv_today = await redis.hgetall(f"analytics:pv:{today}")
        uv_today = await redis.scard(f"analytics:uv:{today}")
        total_pv = await redis.get("analytics:total_pv")
        hourly = await redis.hgetall(f"analytics:hourly:{today}")

        daily_totals: dict[str, int] = {}
        for i in range(7):
            d = (datetime.now(UTC) - timedelta(days=i)).strftime("%Y-%m-%d")
            pv = await redis.hgetall(f"analytics:pv:{d}")
            daily_totals[d] = sum(int(v) for v in pv.values()) if pv else 0

        return {
            "today": {
                "date": today,
                "page_views": {k: int(v) for k, v in pv_today.items()} if pv_today else {},
                "total_views": sum(int(v) for v in pv_today.values()) if pv_today else 0,
                "unique_visitors": uv_today or 0,
                "hourly": {k: int(v) for k, v in hourly.items()} if hourly else {},
            },
            "total_all_time": int(total_pv) if total_pv else 0,
            "last_7_days": daily_totals,
        }
    except Exception as e:
        logger.warning("Analytics summary failed: %s", e)
        return {"error": str(e)}
