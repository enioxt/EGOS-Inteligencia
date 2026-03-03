"""Helpers for provenance/non-repudiation metadata in ETL pipelines."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
import hashlib
import json
from typing import Any


def _normalize(value: Any) -> Any:
    """Normalize values into a deterministic JSON-serializable structure."""
    if isinstance(value, dict):
        return {str(k): _normalize(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list | tuple):
        return [_normalize(v) for v in value]
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    if isinstance(value, Decimal):
        return str(value)
    return value


def canonical_row_json(row: dict[str, Any]) -> str:
    """Return stable JSON representation for hashing raw rows."""
    normalized = _normalize(row)
    return json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    """Return hex SHA-256 for a text value."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def raw_row_hash(row: dict[str, Any]) -> str:
    """Compute a non-repudiation hash for a raw row payload."""
    return sha256_text(canonical_row_json(row))


def source_fingerprint(source_url: str, method: str, collected_at: str) -> str:
    """Compute deterministic fingerprint for a data source snapshot."""
    payload = f"{source_url.strip()}|{method.strip()}|{collected_at.strip()}"
    return sha256_text(payload)


def build_audit_fields(
    *,
    raw_row: dict[str, Any],
    source_url: str,
    method: str,
    collected_at: str | None = None,
) -> dict[str, str]:
    """Build audit metadata to attach to transformed nodes/relationships."""
    verified_at = collected_at or datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "raw_line_hash": raw_row_hash(raw_row),
        "source_url": source_url.strip(),
        "source_method": method.strip() or "unknown",
        "verified_at": verified_at,
        "audit_status": "verified",
        "source_fingerprint": source_fingerprint(source_url, method, verified_at),
    }
