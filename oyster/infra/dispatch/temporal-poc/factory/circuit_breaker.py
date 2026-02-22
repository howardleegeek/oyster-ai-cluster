"""
Circuit Breaker — Ported from Ralph (frankbria/ralph-claude-code).

3-state machine: CLOSED → HALF_OPEN → OPEN
Prevents runaway loops when the factory is stuck.

Key patterns from Ralph:
- No progress detection via git SHA diff
- Same-error deduplication
- Cooldown timer before recovery attempt
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class BreakerState(str, Enum):
    CLOSED = "CLOSED"  # Normal operation
    HALF_OPEN = "HALF_OPEN"  # Testing recovery
    OPEN = "OPEN"  # Halted — waiting for cooldown


@dataclass
class CircuitBreakerSnapshot:
    """Serializable state of the circuit breaker."""

    state: BreakerState = BreakerState.CLOSED
    consecutive_no_progress: int = 0
    consecutive_same_error: int = 0
    last_error_hash: str = ""
    last_progress_cycle: int = 0
    total_opens: int = 0
    opened_at: float = 0.0  # timestamp
    last_transition: str = ""

    def to_dict(self) -> dict:
        return {
            "state": self.state.value,
            "consecutive_no_progress": self.consecutive_no_progress,
            "consecutive_same_error": self.consecutive_same_error,
            "last_error_hash": self.last_error_hash,
            "last_progress_cycle": self.last_progress_cycle,
            "total_opens": self.total_opens,
            "opened_at": self.opened_at,
            "last_transition": self.last_transition,
        }

    @classmethod
    def from_dict(cls, d: dict) -> CircuitBreakerSnapshot:
        return cls(
            state=BreakerState(d.get("state", "CLOSED")),
            consecutive_no_progress=d.get("consecutive_no_progress", 0),
            consecutive_same_error=d.get("consecutive_same_error", 0),
            last_error_hash=d.get("last_error_hash", ""),
            last_progress_cycle=d.get("last_progress_cycle", 0),
            total_opens=d.get("total_opens", 0),
            opened_at=d.get("opened_at", 0.0),
            last_transition=d.get("last_transition", ""),
        )


class CircuitBreaker:
    """
    3-state circuit breaker for the factory loop.

    CLOSED: normal — factory runs cycles.
    HALF_OPEN: testing — one cycle allowed, if it succeeds → CLOSED, if not → OPEN.
    OPEN: halted — no cycles until cooldown expires.

    Transitions:
      CLOSED → OPEN: consecutive_no_progress >= threshold
      OPEN → HALF_OPEN: cooldown_minutes elapsed
      HALF_OPEN → CLOSED: progress detected in test cycle
      HALF_OPEN → OPEN: no progress in test cycle
    """

    def __init__(
        self,
        no_progress_threshold: int = 3,
        same_error_threshold: int = 5,
        cooldown_minutes: int = 30,
        auto_reset: bool = False,
        state_file: Optional[str | Path] = None,
    ):
        self.no_progress_threshold = no_progress_threshold
        self.same_error_threshold = same_error_threshold
        self.cooldown_minutes = cooldown_minutes
        self.auto_reset = auto_reset
        self.state_file = Path(state_file) if state_file else None

        self._snap = CircuitBreakerSnapshot()
        if self.state_file and self.state_file.exists():
            self._load()

    # ── Public API ──

    def should_allow_cycle(self) -> tuple[bool, str]:
        """Check if a cycle should be allowed to run.

        Returns:
            (allowed, reason) — reason is empty if allowed.
        """
        if self._snap.state == BreakerState.CLOSED:
            return True, ""

        if self._snap.state == BreakerState.HALF_OPEN:
            return True, "half_open_test"

        # OPEN — check cooldown
        if self.auto_reset:
            self._transition(BreakerState.HALF_OPEN, "auto_reset")
            return True, "auto_reset_test"

        elapsed = time.time() - self._snap.opened_at
        if elapsed >= self.cooldown_minutes * 60:
            self._transition(BreakerState.HALF_OPEN, "cooldown_expired")
            return True, "cooldown_test"

        remaining = int(self.cooldown_minutes * 60 - elapsed)
        return False, f"open_cooldown_{remaining}s"

    def record_progress(self, cycle: int) -> None:
        """Record that a cycle made progress (files changed, tests passed, etc.)."""
        self._snap.consecutive_no_progress = 0
        self._snap.consecutive_same_error = 0
        self._snap.last_error_hash = ""
        self._snap.last_progress_cycle = cycle

        if self._snap.state in (BreakerState.HALF_OPEN, BreakerState.OPEN):
            self._transition(BreakerState.CLOSED, f"progress_at_cycle_{cycle}")

        self._save()

    def record_no_progress(self, cycle: int, error_summary: str = "") -> None:
        """Record that a cycle made no progress."""
        self._snap.consecutive_no_progress += 1

        # Same-error tracking
        error_hash = str(hash(error_summary)) if error_summary else ""
        if error_hash and error_hash == self._snap.last_error_hash:
            self._snap.consecutive_same_error += 1
        else:
            self._snap.consecutive_same_error = 1 if error_hash else 0
            self._snap.last_error_hash = error_hash

        # Check thresholds
        should_open = False
        reason = ""

        if self._snap.consecutive_no_progress >= self.no_progress_threshold:
            should_open = True
            reason = f"no_progress_{self._snap.consecutive_no_progress}_cycles"

        if self._snap.consecutive_same_error >= self.same_error_threshold:
            should_open = True
            reason = f"same_error_{self._snap.consecutive_same_error}_times"

        if should_open and self._snap.state != BreakerState.OPEN:
            self._transition(BreakerState.OPEN, reason)

        # HALF_OPEN test failed → back to OPEN
        if self._snap.state == BreakerState.HALF_OPEN and not should_open:
            self._transition(BreakerState.OPEN, "half_open_test_failed")

        self._save()

    def reset(self) -> None:
        """Manual reset — force back to CLOSED."""
        self._snap = CircuitBreakerSnapshot()
        self._snap.last_transition = "manual_reset"
        self._save()

    @property
    def state(self) -> BreakerState:
        return self._snap.state

    @property
    def snapshot(self) -> CircuitBreakerSnapshot:
        return self._snap

    # ── Internal ──

    def _transition(self, new_state: BreakerState, reason: str) -> None:
        old = self._snap.state
        self._snap.state = new_state
        self._snap.last_transition = f"{old.value}->{new_state.value}:{reason}"

        if new_state == BreakerState.OPEN:
            self._snap.opened_at = time.time()
            self._snap.total_opens += 1

    def _save(self) -> None:
        if not self.state_file:
            return
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(self._snap.to_dict(), f, indent=2)

    def _load(self) -> None:
        if not self.state_file or not self.state_file.exists():
            return
        try:
            with open(self.state_file) as f:
                self._snap = CircuitBreakerSnapshot.from_dict(json.load(f))
        except (json.JSONDecodeError, KeyError):
            self._snap = CircuitBreakerSnapshot()
