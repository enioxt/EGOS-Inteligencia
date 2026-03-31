"""
Guard Brasil — Python middleware for EGOS Guard Brasil API.

Provides PII detection, LGPD compliance validation, and ATRiAN ethical checks
via the Guard Brasil REST API (guard.egos.ia.br).

Usage in ETL pipelines:
    from bracc_etl.guard import GuardBrasilClient, guard_dataframe

    client = GuardBrasilClient()
    result = client.inspect("CPF do titular: 123.456.789-00")
    if not result["safe"]:
        print(result["output"])  # masked text

    # Bulk: inspect a DataFrame column
    df = guard_dataframe(df, columns=["nome", "descricao"], client=client)

Environment:
    GUARD_BRASIL_URL     — API base URL (default: https://guard.egos.ia.br)
    GUARD_BRASIL_API_KEY — Bearer token for authentication
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any

import requests

logger = logging.getLogger(__name__)

# ── Configuration ────────────────────────────────────────────────────────────

GUARD_BRASIL_URL = os.getenv("GUARD_BRASIL_URL", "https://guard.egos.ia.br")
GUARD_BRASIL_API_KEY = os.getenv("GUARD_BRASIL_API_KEY", "")

# ── Offline PII patterns (fallback when API is unreachable) ──────────────────

_OFFLINE_PATTERNS: dict[str, re.Pattern[str]] = {
    "cpf": re.compile(r"\b\d{3}[.\s-]?\d{3}[.\s-]?\d{3}[.\s/-]?\d{2}\b"),
    "cnpj": re.compile(r"\b\d{2}[.\s]?\d{3}[.\s]?\d{3}[/\s]?\d{4}[-.\s]?\d{2}\b"),
    "rg": re.compile(r"\b(?:RG|rg|Rg)[:\s]*\d{1,2}[.\s]?\d{3}[.\s]?\d{3}[.\s-]?\d?\b", re.IGNORECASE),
    "masp": re.compile(r"\b(?:MASP|masp|Masp)[:\s]*\d{4,8}[.\s-]?\d{0,2}\b", re.IGNORECASE),
    "reds": re.compile(r"\b(?:REDS|reds|Reds)[:\s]*\d{4,}[-./]?\d{0,}\b", re.IGNORECASE),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "telefone": re.compile(r"\b(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}[-.\s]?\d{4}\b"),
}

_OFFLINE_MASKS: dict[str, str] = {
    "cpf": "[CPF REMOVIDO]",
    "cnpj": "[CNPJ REMOVIDO]",
    "rg": "[RG REMOVIDO]",
    "masp": "[MASP REMOVIDO]",
    "reds": "[REDS REMOVIDO]",
    "email": "[EMAIL REMOVIDO]",
    "telefone": "[TELEFONE REMOVIDO]",
}


# ── Types ────────────────────────────────────────────────────────────────────


@dataclass
class GuardResult:
    """Result from a Guard Brasil inspection."""

    safe: bool
    blocked: bool
    output: str
    summary: str
    original: str
    pii_count: int = 0
    atrian_passed: bool = True
    atrian_score: float = 100.0
    sensitivity_level: str = "none"
    duration_ms: int = 0
    offline: bool = False
    raw: dict[str, Any] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return self.safe


# ── Client ───────────────────────────────────────────────────────────────────


class GuardBrasilClient:
    """HTTP client for the Guard Brasil REST API.

    Falls back to offline regex-based PII detection when the API is unreachable.
    This ensures ETL pipelines never fail due to Guard Brasil being down.
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 5.0,
        pri_strategy: str = "balanced",
    ) -> None:
        self.base_url = (base_url or GUARD_BRASIL_URL).rstrip("/")
        self.api_key = api_key or GUARD_BRASIL_API_KEY
        self.timeout = timeout
        self.pri_strategy = pri_strategy
        self._session = requests.Session()
        if self.api_key:
            self._session.headers["Authorization"] = f"Bearer {self.api_key}"
        self._session.headers["Content-Type"] = "application/json"
        self._session.headers["User-Agent"] = "egos-inteligencia-etl/1.0"

    def inspect(
        self,
        text: str,
        *,
        session_id: str | None = None,
        pii_types: list[str] | None = None,
        pri_strategy: str | None = None,
    ) -> GuardResult:
        """Inspect text via Guard Brasil API. Falls back to offline if unavailable."""
        if not text or not text.strip():
            return GuardResult(
                safe=True, blocked=False, output=text,
                summary="Empty text — skipped.", original=text,
            )

        try:
            payload: dict[str, Any] = {"text": text}
            if session_id:
                payload["sessionId"] = session_id
            if pii_types:
                payload["pii_types"] = pii_types
            payload["pri_strategy"] = pri_strategy or self.pri_strategy

            resp = self._session.post(
                f"{self.base_url}/v1/inspect",
                json=payload,
                timeout=self.timeout,
            )

            if resp.status_code == 422:
                data = resp.json()
                return GuardResult(
                    safe=False, blocked=True, output="[BLOQUEADO POR PRI]",
                    summary=f"PRI blocked: {data.get('pri', {}).get('reasoning', 'unknown')}",
                    original=text, raw=data, offline=False,
                )

            if resp.status_code in (200, 202):
                data = resp.json()
                return GuardResult(
                    safe=data.get("safe", False),
                    blocked=data.get("blocked", False),
                    output=data.get("output", text),
                    summary=data.get("summary", ""),
                    original=text,
                    pii_count=data.get("masking", {}).get("findingCount", 0),
                    atrian_passed=data.get("atrian", {}).get("passed", True),
                    atrian_score=data.get("atrian", {}).get("score", 100.0),
                    sensitivity_level=data.get("masking", {}).get("sensitivityLevel", "none"),
                    duration_ms=data.get("meta", {}).get("durationMs", 0),
                    offline=False,
                    raw=data,
                )

            logger.warning("Guard Brasil returned %d — falling back to offline", resp.status_code)

        except (requests.ConnectionError, requests.Timeout, requests.RequestException) as exc:
            logger.warning("Guard Brasil unreachable (%s) — using offline PII detection", exc)

        return self._offline_inspect(text)

    def _offline_inspect(self, text: str) -> GuardResult:
        """Regex-based PII detection — mirrors Guard Brasil patterns offline."""
        findings: list[dict[str, str]] = []
        masked = text

        for pii_id, pattern in _OFFLINE_PATTERNS.items():
            for match in pattern.finditer(masked):
                findings.append({"type": pii_id, "matched": match.group()})
            masked = pattern.sub(_OFFLINE_MASKS.get(pii_id, "[REMOVIDO]"), masked)

        safe = len(findings) == 0
        return GuardResult(
            safe=safe,
            blocked=False,
            output=masked,
            summary=f"Offline: {len(findings)} PII finding(s)" if findings else "Offline: clean",
            original=text,
            pii_count=len(findings),
            sensitivity_level="high" if any(f["type"] in ("cpf", "rg", "masp") for f in findings) else "low",
            offline=True,
            raw={"findings": findings},
        )

    def health(self) -> dict[str, Any]:
        """Check Guard Brasil API health."""
        try:
            resp = self._session.get(f"{self.base_url}/health", timeout=3.0)
            return resp.json()
        except Exception as exc:
            return {"status": "unreachable", "error": str(exc)}


# ── DataFrame integration ────────────────────────────────────────────────────


def guard_dataframe(
    df: Any,
    columns: list[str],
    client: GuardBrasilClient | None = None,
    mask_in_place: bool = True,
    add_guard_column: bool = True,
) -> Any:
    """Inspect and optionally mask PII in specific DataFrame columns.

    Args:
        df: pandas DataFrame to inspect
        columns: column names containing text to guard
        client: GuardBrasilClient instance (creates default if None)
        mask_in_place: if True, replaces column values with masked output
        add_guard_column: if True, adds a '__guard_pii_count' column

    Returns:
        The DataFrame (modified in place if mask_in_place=True)
    """
    if client is None:
        client = GuardBrasilClient()

    pii_counts: list[int] = [0] * len(df)

    for col in columns:
        if col not in df.columns:
            logger.warning("Column '%s' not in DataFrame — skipping guard", col)
            continue

        for idx in range(len(df)):
            val = df.iloc[idx][col]
            if not isinstance(val, str) or not val.strip():
                continue

            result = client.inspect(val)
            pii_counts[idx] += result.pii_count

            if mask_in_place and not result.safe:
                df.at[df.index[idx], col] = result.output

    if add_guard_column:
        df["__guard_pii_count"] = pii_counts

    total_pii = sum(pii_counts)
    if total_pii > 0:
        logger.info(
            "Guard Brasil: %d PII finding(s) across %d rows in columns %s",
            total_pii, sum(1 for c in pii_counts if c > 0), columns,
        )

    return df


# ── Report validation ────────────────────────────────────────────────────────


def validate_report_text(
    text: str,
    client: GuardBrasilClient | None = None,
    strict: bool = True,
) -> GuardResult:
    """Validate a report's full text for PII leaks and ATRiAN violations.

    In strict mode (default), any PII finding or ATRiAN violation causes
    the result to be marked as unsafe.

    Args:
        text: full report text to validate
        client: GuardBrasilClient instance
        strict: if True, treat any finding as unsafe (default for reports)

    Returns:
        GuardResult with validation details
    """
    if client is None:
        client = GuardBrasilClient()

    result = client.inspect(text, pri_strategy="paranoid" if strict else "balanced")

    if strict and result.pii_count > 0:
        result.safe = False
        result.summary = f"STRICT: {result.pii_count} PII finding(s) — report blocked"

    return result
