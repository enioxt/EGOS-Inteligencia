"""Lightweight circuit breaker for external API calls.

Tracks failures per API host. After FAILURE_THRESHOLD failures within
WINDOW_SECONDS, the circuit opens and subsequent calls are short-circuited
for COOLDOWN_SECONDS before allowing a retry.

States: CLOSED (normal) → OPEN (failing) → HALF_OPEN (one retry allowed)

Usage:
    from bracc.services.circuit_breaker import circuit_breaker

    if not circuit_breaker.allow("api.portaldatransparencia.gov.br"):
        return {"error": "API temporarily unavailable"}
    try:
        result = await call_api(...)
        circuit_breaker.record_success("api.portaldatransparencia.gov.br")
    except Exception:
        circuit_breaker.record_failure("api.portaldatransparencia.gov.br")
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitStats:
    failures: int = 0
    successes: int = 0
    last_failure_time: float = 0.0
    state: CircuitState = CircuitState.CLOSED
    opened_at: float = 0.0
    failure_times: list[float] = field(default_factory=list)


class CircuitBreaker:
    """Per-host circuit breaker with configurable thresholds."""

    def __init__(
        self,
        failure_threshold: int = 5,
        window_seconds: float = 120.0,
        cooldown_seconds: float = 60.0,
    ):
        self._threshold = failure_threshold
        self._window = window_seconds
        self._cooldown = cooldown_seconds
        self._circuits: dict[str, CircuitStats] = {}

    def _get_circuit(self, host: str) -> CircuitStats:
        if host not in self._circuits:
            self._circuits[host] = CircuitStats()
        return self._circuits[host]

    def _prune_old_failures(self, circuit: CircuitStats) -> None:
        """Remove failures outside the time window."""
        cutoff = time.time() - self._window
        circuit.failure_times = [t for t in circuit.failure_times if t > cutoff]
        circuit.failures = len(circuit.failure_times)

    def allow(self, host: str) -> bool:
        """Check if a request to this host should be allowed."""
        circuit = self._get_circuit(host)
        now = time.time()

        if circuit.state == CircuitState.CLOSED:
            return True

        if circuit.state == CircuitState.OPEN:
            if now - circuit.opened_at >= self._cooldown:
                circuit.state = CircuitState.HALF_OPEN
                logger.info("Circuit HALF_OPEN for %s (allowing one retry)", host)
                return True
            return False

        if circuit.state == CircuitState.HALF_OPEN:
            return True

        return True

    def record_success(self, host: str) -> None:
        """Record a successful call — reset circuit if half-open."""
        circuit = self._get_circuit(host)
        circuit.successes += 1
        if circuit.state in (CircuitState.HALF_OPEN, CircuitState.OPEN):
            logger.info("Circuit CLOSED for %s (recovered)", host)
            circuit.state = CircuitState.CLOSED
            circuit.failures = 0
            circuit.failure_times = []

    def record_failure(self, host: str) -> None:
        """Record a failed call — may open the circuit."""
        circuit = self._get_circuit(host)
        now = time.time()
        circuit.failure_times.append(now)
        circuit.last_failure_time = now
        self._prune_old_failures(circuit)

        if circuit.state == CircuitState.HALF_OPEN:
            circuit.state = CircuitState.OPEN
            circuit.opened_at = now
            logger.warning("Circuit OPEN for %s (half-open retry failed)", host)
            return

        if circuit.failures >= self._threshold:
            circuit.state = CircuitState.OPEN
            circuit.opened_at = now
            logger.warning(
                "Circuit OPEN for %s (%d failures in %ds window)",
                host, circuit.failures, int(self._window),
            )

    def get_status(self) -> dict[str, dict]:
        """Return status of all tracked circuits for monitoring."""
        result = {}
        now = time.time()
        for host, circuit in self._circuits.items():
            self._prune_old_failures(circuit)
            result[host] = {
                "state": circuit.state.value,
                "failures_in_window": circuit.failures,
                "total_successes": circuit.successes,
                "cooldown_remaining": max(0, self._cooldown - (now - circuit.opened_at))
                if circuit.state == CircuitState.OPEN else 0,
            }
        return result

    def reset(self, host: str = "") -> None:
        """Manually reset a circuit (or all circuits)."""
        if host:
            self._circuits.pop(host, None)
        else:
            self._circuits.clear()


# Singleton — 5 failures in 2 min → 60s cooldown
circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    window_seconds=120.0,
    cooldown_seconds=60.0,
)
