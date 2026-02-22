"""
Evolution Memory — Trajectory tracking + Thompson Sampling template selection.

Sources:
- OpenAI GEPA: VersionedPrompt pattern
- HGM: Thompson Sampling + CMP (Clade-Metaproductivity) scoring
- SWE-agent: Trajectory JSONL logging
"""

from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class TrajectoryStep:
    """One step in a task execution."""

    timestamp: float
    phase: str  # "think" | "build" | "review" | "learn"
    action: str
    result: str
    duration_seconds: float = 0.0
    tokens_used: int = 0
    error: str = ""


@dataclass
class TaskTrajectory:
    """Complete execution trajectory for one task."""

    task_id: str
    project: str
    spec_content: str
    template_id: str  # which prompt template generated this spec
    steps: list[TrajectoryStep] = field(default_factory=list)
    outcome: str = ""  # "success" | "failed" | "needs_human"
    failure_reason: str = ""
    advisor_consensus: str = ""
    total_tokens: int = 0
    total_duration: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0

    def add_step(self, step: TrajectoryStep) -> None:
        self.steps.append(step)
        self.total_tokens += step.tokens_used
        self.total_duration += step.duration_seconds

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "project": self.project,
            "spec_content": self.spec_content[:500],
            "template_id": self.template_id,
            "outcome": self.outcome,
            "failure_reason": self.failure_reason,
            "advisor_consensus": self.advisor_consensus[:500],
            "total_tokens": self.total_tokens,
            "total_duration": self.total_duration,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "step_count": len(self.steps),
            "steps": [
                {
                    "phase": s.phase,
                    "action": s.action[:200],
                    "result": s.result[:200],
                    "duration": s.duration_seconds,
                    "error": s.error[:200] if s.error else "",
                }
                for s in self.steps
            ],
        }


@dataclass
class PromptVersion:
    """Immutable snapshot of a prompt template — from OpenAI GEPA VersionedPrompt."""

    version: int
    template_id: str
    content: str
    created_at: float
    metadata: dict = field(default_factory=dict)
    # Accumulated stats
    successes: int = 0
    failures: int = 0

    @property
    def total_uses(self) -> int:
        return self.successes + self.failures

    @property
    def success_rate(self) -> float:
        if self.total_uses == 0:
            return 0.5  # prior
        return self.successes / self.total_uses


@dataclass
class TemplateStats:
    """Thompson Sampling stats for a spec template — from HGM CMP pattern."""

    template_id: str
    description: str
    successes: int = 0  # alpha - 1 in Beta distribution
    failures: int = 0  # beta - 1 in Beta distribution

    def thompson_sample(self) -> float:
        """Sample from Beta(alpha, beta) for Thompson Sampling."""
        alpha = 1 + self.successes
        beta = 1 + self.failures
        return random.betavariate(alpha, beta)

    @property
    def cmp_score(self) -> float:
        """Clade-Metaproductivity — success rate of descendants."""
        total = self.successes + self.failures
        if total == 0:
            return 0.5
        return self.successes / total


class EvolutionMemory:
    """
    Persistent memory for factory evolution.

    Stores:
    - Task trajectories (for learning what works/fails)
    - Prompt template versions (for GEPA-style evolution)
    - Template stats (for Thompson Sampling selection)
    """

    def __init__(
        self,
        trajectory_dir: str | Path,
        prompts_dir: str | Path,
    ):
        self.trajectory_dir = Path(trajectory_dir)
        self.prompts_dir = Path(prompts_dir)
        self.trajectory_dir.mkdir(parents=True, exist_ok=True)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)

        self._templates: dict[str, TemplateStats] = {}
        self._prompt_versions: dict[str, list[PromptVersion]] = {}
        self._load_templates()

    # ── Trajectory logging (SWE-agent pattern) ──

    def save_trajectory(self, trajectory: TaskTrajectory) -> Path:
        """Save a task trajectory to disk."""
        project_dir = self.trajectory_dir / trajectory.project
        project_dir.mkdir(parents=True, exist_ok=True)
        path = project_dir / f"{trajectory.task_id}.json"
        with open(path, "w") as f:
            json.dump(trajectory.to_dict(), f, indent=2)
        return path

    def load_trajectories(
        self, project: str, limit: int = 50
    ) -> list[dict]:
        """Load recent trajectories for a project."""
        project_dir = self.trajectory_dir / project
        if not project_dir.exists():
            return []

        files = sorted(project_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        results = []
        for f in files[:limit]:
            try:
                with open(f) as fh:
                    results.append(json.load(fh))
            except (json.JSONDecodeError, OSError):
                continue
        return results

    def get_failure_patterns(self, project: str, limit: int = 20) -> list[dict]:
        """Get recent failure trajectories for learning."""
        trajs = self.load_trajectories(project, limit=limit * 2)
        return [t for t in trajs if t.get("outcome") == "failed"][:limit]

    # ── Thompson Sampling template selection (HGM pattern) ──

    def register_template(self, template_id: str, description: str) -> None:
        """Register a new spec template for tracking."""
        if template_id not in self._templates:
            self._templates[template_id] = TemplateStats(
                template_id=template_id, description=description
            )
            self._save_templates()

    def record_template_outcome(
        self, template_id: str, success: bool
    ) -> None:
        """Record a task outcome for a template."""
        if template_id not in self._templates:
            self._templates[template_id] = TemplateStats(
                template_id=template_id, description="auto-registered"
            )

        if success:
            self._templates[template_id].successes += 1
        else:
            self._templates[template_id].failures += 1

        self._save_templates()

    def select_best_template(
        self, candidates: Optional[list[str]] = None
    ) -> Optional[str]:
        """Select best template using Thompson Sampling."""
        pool = self._templates
        if candidates:
            pool = {k: v for k, v in pool.items() if k in candidates}

        if not pool:
            return None

        # Thompson sample: draw from Beta distribution for each
        sampled = {
            tid: stats.thompson_sample()
            for tid, stats in pool.items()
        }
        return max(sampled, key=sampled.get)

    def get_template_stats(self) -> list[dict]:
        """Get all template stats for reporting."""
        return [
            {
                "template_id": t.template_id,
                "description": t.description,
                "successes": t.successes,
                "failures": t.failures,
                "cmp": round(t.cmp_score, 3),
            }
            for t in sorted(
                self._templates.values(),
                key=lambda t: t.cmp_score,
                reverse=True,
            )
        ]

    # ── Prompt version management (GEPA VersionedPrompt) ──

    def save_prompt_version(
        self,
        template_id: str,
        content: str,
        metadata: Optional[dict] = None,
    ) -> PromptVersion:
        """Save a new version of a prompt template."""
        versions = self._prompt_versions.get(template_id, [])
        version_num = len(versions) + 1

        pv = PromptVersion(
            version=version_num,
            template_id=template_id,
            content=content,
            created_at=time.time(),
            metadata=metadata or {},
        )
        versions.append(pv)
        self._prompt_versions[template_id] = versions

        # Persist
        version_dir = self.prompts_dir / template_id
        version_dir.mkdir(parents=True, exist_ok=True)
        path = version_dir / f"v{version_num}.json"
        with open(path, "w") as f:
            json.dump(
                {
                    "version": pv.version,
                    "template_id": pv.template_id,
                    "content": pv.content,
                    "created_at": pv.created_at,
                    "metadata": pv.metadata,
                    "successes": pv.successes,
                    "failures": pv.failures,
                },
                f,
                indent=2,
            )
        return pv

    def get_current_prompt(self, template_id: str) -> Optional[str]:
        """Get the latest version of a prompt template."""
        versions = self._prompt_versions.get(template_id, [])
        if not versions:
            # Try loading from disk
            version_dir = self.prompts_dir / template_id
            if version_dir.exists():
                files = sorted(version_dir.glob("v*.json"))
                if files:
                    with open(files[-1]) as f:
                        data = json.load(f)
                    return data.get("content", "")
            return None
        return versions[-1].content

    # ── Persistence ──

    def _save_templates(self) -> None:
        path = self.trajectory_dir / "_template_stats.json"
        with open(path, "w") as f:
            json.dump(
                {
                    tid: {
                        "template_id": t.template_id,
                        "description": t.description,
                        "successes": t.successes,
                        "failures": t.failures,
                    }
                    for tid, t in self._templates.items()
                },
                f,
                indent=2,
            )

    def _load_templates(self) -> None:
        path = self.trajectory_dir / "_template_stats.json"
        if not path.exists():
            return
        try:
            with open(path) as f:
                data = json.load(f)
            for tid, info in data.items():
                self._templates[tid] = TemplateStats(**info)
        except (json.JSONDecodeError, OSError, TypeError):
            pass
