"""Prompt injection detection middleware.

Soft defense-in-depth: logs suspicious inputs without blocking them.
Patterns based on known prompt injection techniques.
"""

import logging
import re

_logger = logging.getLogger(__name__)

_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions?|prompts?|rules?)", re.I),
    re.compile(r"(disregard|forget|override)\s+(your|the|all)\s+(instructions?|rules?|prompts?)", re.I),
    re.compile(r"you\s+are\s+now\s+(a|an|the)\s+", re.I),
    re.compile(r"system\s*prompt", re.I),
    re.compile(r"reveal\s+(your|the)\s+(system|initial|original)\s+(prompt|instructions?|message)", re.I),
    re.compile(r"(print|show|output|repeat)\s+(your|the)\s+(system|initial)\s+(prompt|instructions?)", re.I),
    re.compile(r"<\|?(system|im_start|endoftext)\|?>", re.I),
    re.compile(r"\[INST\]|\[/INST\]|<<SYS>>|<</SYS>>", re.I),
    re.compile(r"jailbreak|DAN\s*mode|evil\s*mode|developer\s*mode", re.I),
    re.compile(r"pretend\s+you\s+(are|have)\s+no\s+(restrictions?|rules?|limits?)", re.I),
]


def check_injection(text: str) -> str | None:
    """Return the matched pattern name if injection detected, else None."""
    for pattern in _INJECTION_PATTERNS:
        match = pattern.search(text)
        if match:
            _logger.warning(
                "Prompt injection pattern detected: %r in input: %.100s",
                pattern.pattern,
                text,
            )
            return pattern.pattern
    return None
