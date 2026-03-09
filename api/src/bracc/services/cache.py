"""Redis cache-aside layer for EGOS Inteligência.

Provides async cache with configurable TTL per key prefix.
Gracefully degrades — all operations are no-ops if Redis is unavailable.
"""

import hashlib
import json
import logging
from typing import Any

import redis.asyncio as redis

from bracc.config import settings

logger = logging.getLogger(__name__)

# TTL configuration per prefix (seconds)
TTL_CONFIG = {
    "search": 120,      # 2 min — search results change rarely
    "entity": 300,      # 5 min — entity details are stable
    "stats": 60,        # 1 min — stats update with ETL progress
    "chat": 0,          # no cache — conversations are unique
    "connections": 180,  # 3 min — entity connections
}

# Stats tracking
_stats = {"hits": 0, "misses": 0, "errors": 0, "sets": 0}


class CacheService:
    """Async Redis cache with graceful degradation."""

    def __init__(self) -> None:
        self._client: redis.Redis | None = None
        self._available = False

    async def connect(self, url: str = "") -> None:
        redis_url = url or getattr(settings, "redis_url", "") or "redis://localhost:6379/0"
        try:
            self._client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=3,
                socket_timeout=2,
                retry_on_timeout=True,
            )
            await self._client.ping()
            self._available = True
            logger.info("Redis cache connected: %s", redis_url.split("@")[-1])
        except Exception as e:
            logger.warning("Redis unavailable, cache disabled: %s", e)
            self._available = False

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
            self._available = False

    @staticmethod
    def _make_key(prefix: str, params: dict[str, Any]) -> str:
        raw = json.dumps(params, sort_keys=True, default=str)
        h = hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()[:12]
        return f"egos:{prefix}:{h}"

    async def get(self, prefix: str, params: dict[str, Any]) -> Any | None:
        if not self._available or prefix not in TTL_CONFIG or TTL_CONFIG[prefix] == 0:
            return None
        try:
            key = self._make_key(prefix, params)
            raw = await self._client.get(key)  # type: ignore[union-attr]
            if raw is not None:
                _stats["hits"] += 1
                return json.loads(raw)
            _stats["misses"] += 1
            return None
        except Exception:
            _stats["errors"] += 1
            return None

    async def set(self, prefix: str, params: dict[str, Any], value: Any) -> None:
        if not self._available or prefix not in TTL_CONFIG or TTL_CONFIG[prefix] == 0:
            return
        try:
            key = self._make_key(prefix, params)
            ttl = TTL_CONFIG[prefix]
            raw = json.dumps(value, default=str, ensure_ascii=False)
            if len(raw) > 500_000:  # skip caching >500KB responses
                return
            await self._client.setex(key, ttl, raw)  # type: ignore[union-attr]
            _stats["sets"] += 1
        except Exception:
            _stats["errors"] += 1

    def get_stats(self) -> dict[str, Any]:
        total = _stats["hits"] + _stats["misses"]
        hit_rate = (_stats["hits"] / total * 100) if total > 0 else 0.0
        return {
            **_stats,
            "total_requests": total,
            "hit_rate_pct": round(hit_rate, 1),
            "available": self._available,
            "ttl_config": TTL_CONFIG,
        }

    async def flush(self) -> int:
        if not self._available:
            return 0
        try:
            keys = []
            async for key in self._client.scan_iter("egos:*"):  # type: ignore[union-attr]
                keys.append(key)
            if keys:
                await self._client.delete(*keys)  # type: ignore[union-attr]
            return len(keys)
        except Exception:
            return 0


# Singleton instance
cache = CacheService()
