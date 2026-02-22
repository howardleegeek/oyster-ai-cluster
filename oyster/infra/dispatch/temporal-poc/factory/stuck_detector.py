"""
Stuck Detector — Ported from OpenHands (All-Hands-AI/OpenHands).

Detects 5 patterns of agent stuck-in-loop behavior:
1. Repeating action-observation pairs
2. Repeating action-error pairs
3. Agent monologue (same message to itself)
4. Alternating between two states
5. Context window loop (condensation repeats)

Adapted for spec execution context rather than interactive agent context.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Optional


@dataclass
class StepRecord:
    """One step in a task execution trajectory."""

    step_num: int
    action: str  # what the agent did
    observation: str  # what happened
    is_error: bool = False
    truncated: bool = False  # observation was truncated


class StuckPattern:
    """Detected stuck pattern with details."""

    def __init__(self, pattern_name: str, evidence: str, severity: int = 1):
        self.pattern_name = pattern_name
        self.evidence = evidence
        self.severity = severity  # 1=warning, 2=should_stop, 3=must_stop

    def __repr__(self) -> str:
        return f"StuckPattern({self.pattern_name}, severity={self.severity})"


class StuckDetector:
    """
    Analyzes a trajectory of steps to detect stuck-loop patterns.

    Usage:
        detector = StuckDetector()
        for step in trajectory:
            detector.add_step(step)
            pattern = detector.check()
            if pattern and pattern.severity >= 2:
                # kill the task
    """

    def __init__(
        self,
        repeat_threshold: int = 4,
        error_repeat_threshold: int = 3,
        monologue_threshold: int = 3,
        alternating_threshold: int = 6,
        condensation_threshold: int = 10,
    ):
        self.repeat_threshold = repeat_threshold
        self.error_repeat_threshold = error_repeat_threshold
        self.monologue_threshold = monologue_threshold
        self.alternating_threshold = alternating_threshold
        self.condensation_threshold = condensation_threshold

        self._steps: list[StepRecord] = []

    def add_step(self, step: StepRecord) -> None:
        """Add a step to the trajectory."""
        self._steps.append(step)

    def check(self) -> Optional[StuckPattern]:
        """Check all patterns. Returns the most severe match, or None."""
        if len(self._steps) < 3:
            return None

        patterns = [
            self._check_repeating_action_observation(),
            self._check_repeating_action_error(),
            self._check_monologue(),
            self._check_alternating(),
            self._check_condensation_loop(),
        ]

        matches = [p for p in patterns if p is not None]
        if not matches:
            return None

        return max(matches, key=lambda p: p.severity)

    def reset(self) -> None:
        """Clear all recorded steps."""
        self._steps.clear()

    # ── Pattern detectors ──

    def _check_repeating_action_observation(self) -> Optional[StuckPattern]:
        """Pattern 1: Same action → same observation, N times in a row."""
        if len(self._steps) < self.repeat_threshold:
            return None

        recent = self._steps[-self.repeat_threshold :]
        pairs = [(s.action, s.observation) for s in recent]

        if len(set(pairs)) == 1:
            return StuckPattern(
                "repeating_action_observation",
                f"Same action-observation pair repeated {self.repeat_threshold}x: "
                f"{pairs[0][0][:80]}...",
                severity=2,
            )
        return None

    def _check_repeating_action_error(self) -> Optional[StuckPattern]:
        """Pattern 2: Same action → error, N times in a row."""
        if len(self._steps) < self.error_repeat_threshold:
            return None

        recent = self._steps[-self.error_repeat_threshold :]

        if not all(s.is_error for s in recent):
            return None

        actions = [s.action for s in recent]
        if len(set(actions)) == 1:
            return StuckPattern(
                "repeating_action_error",
                f"Same action failing {self.error_repeat_threshold}x: "
                f"{actions[0][:80]}...",
                severity=3,
            )
        return None

    def _check_monologue(self) -> Optional[StuckPattern]:
        """Pattern 3: Agent sends identical message to itself N times."""
        if len(self._steps) < self.monologue_threshold:
            return None

        recent = self._steps[-self.monologue_threshold :]
        actions = [s.action for s in recent]

        if len(set(actions)) == 1 and not any(s.is_error for s in recent):
            return StuckPattern(
                "monologue",
                f"Agent repeating same action {self.monologue_threshold}x "
                f"without errors: {actions[0][:80]}...",
                severity=2,
            )
        return None

    def _check_alternating(self) -> Optional[StuckPattern]:
        """Pattern 4: A→B→A→B alternation for N steps."""
        if len(self._steps) < self.alternating_threshold:
            return None

        recent = self._steps[-self.alternating_threshold :]
        pairs = [(s.action, s.observation) for s in recent]

        # Check if we see only 2 distinct pairs alternating
        unique_pairs = set(pairs)
        if len(unique_pairs) == 2:
            pair_list = list(unique_pairs)
            expected_alternation = [
                pair_list[i % 2] for i in range(len(pairs))
            ]
            reverse_alternation = [
                pair_list[(i + 1) % 2] for i in range(len(pairs))
            ]

            if pairs == expected_alternation or pairs == reverse_alternation:
                return StuckPattern(
                    "alternating",
                    f"Alternating between 2 states for "
                    f"{self.alternating_threshold} steps",
                    severity=2,
                )
        return None

    def _check_condensation_loop(self) -> Optional[StuckPattern]:
        """Pattern 5: Context window condensation happening too often."""
        if len(self._steps) < self.condensation_threshold:
            return None

        recent = self._steps[-self.condensation_threshold :]
        truncated_count = sum(1 for s in recent if s.truncated)

        if truncated_count >= self.condensation_threshold * 0.8:
            return StuckPattern(
                "condensation_loop",
                f"{truncated_count}/{self.condensation_threshold} recent steps "
                f"had truncated observations — likely context window thrashing",
                severity=3,
            )
        return None

    @property
    def step_count(self) -> int:
        return len(self._steps)

    def summary(self) -> dict:
        """Return a summary of the trajectory for debugging."""
        if not self._steps:
            return {"steps": 0}

        error_count = sum(1 for s in self._steps if s.is_error)
        action_counts = Counter(s.action[:50] for s in self._steps)

        return {
            "steps": len(self._steps),
            "errors": error_count,
            "unique_actions": len(action_counts),
            "most_common_action": action_counts.most_common(1)[0]
            if action_counts
            else None,
        }
