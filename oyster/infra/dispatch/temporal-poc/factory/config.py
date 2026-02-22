"""
Factory Configuration — SWE-agent style declarative YAML config.

All factory behavior controlled from one config file.
No scattered env vars or hardcoded values.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class ProjectConfig:
    """Per-project configuration."""

    name: str
    repo_url: str
    repo_local: str
    specs_dir: str
    main_branch: str = "main"
    max_reflections: int = 3  # Aider pattern: bounded self-debug
    max_concurrent_tasks: int = 8
    cost_limit_per_task: float = 0.50  # USD per task
    estimated_minutes_default: int = 30


@dataclass
class AdvisorConfig:
    """Configuration for each advisor in the think phase."""

    name: str
    type: str  # "opus" | "codex" | "antigravity"
    endpoint: str = ""
    api_key_env: str = ""
    model: str = ""
    timeout_seconds: int = 120
    enabled: bool = True


@dataclass
class CircuitBreakerConfig:
    """Ralph-style circuit breaker settings."""

    no_progress_threshold: int = 3  # consecutive cycles with no progress → OPEN
    same_error_threshold: int = 5  # consecutive same error → OPEN
    cooldown_minutes: int = 30  # OPEN → HALF_OPEN after this
    auto_reset: bool = False  # bypass cooldown for dev


@dataclass
class LearnConfig:
    """Evolution/learning phase settings."""

    enabled: bool = True
    trajectory_dir: str = ""  # where to store trajectories
    evolve_every_n_cycles: int = 10  # run GEPA every N cycles
    thompson_enabled: bool = True  # use Thompson Sampling for template selection
    versioned_prompts_dir: str = ""  # where to store prompt versions


@dataclass
class FactoryConfig:
    """Top-level factory configuration."""

    # Projects to iterate on (pilot: 2)
    projects: list[ProjectConfig] = field(default_factory=list)

    # Advisors
    advisors: list[AdvisorConfig] = field(default_factory=list)

    # Temporal
    temporal_host: str = "localhost:7233"
    task_queue: str = "factory-tasks"

    # Cycle timing
    cycle_interval_seconds: int = 60
    think_timeout_minutes: int = 30
    build_timeout_minutes: int = 120
    review_timeout_minutes: int = 30

    # Circuit breaker
    circuit_breaker: CircuitBreakerConfig = field(
        default_factory=CircuitBreakerConfig
    )

    # Learning
    learn: LearnConfig = field(default_factory=LearnConfig)

    # Limits
    max_cycles_per_day: int = 200
    max_specs_per_cycle: int = 10
    max_total_cost_per_day: float = 50.0  # USD

    @classmethod
    def from_yaml(cls, path: str | Path) -> FactoryConfig:
        """Load config from YAML file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config not found: {path}")

        with open(path) as f:
            raw = yaml.safe_load(f)

        projects = []
        for p in raw.get("projects", []):
            # Expand ~ in paths
            for key in ("repo_local", "specs_dir"):
                if key in p and isinstance(p[key], str):
                    p[key] = str(Path(p[key]).expanduser())
            projects.append(ProjectConfig(**p))
        advisors = [
            AdvisorConfig(**a) for a in raw.get("advisors", [])
        ]
        cb_raw = raw.get("circuit_breaker", {})
        learn_raw = raw.get("learn", {})
        # Expand ~ in learn paths
        for key in ("trajectory_dir", "versioned_prompts_dir"):
            if key in learn_raw and isinstance(learn_raw[key], str):
                learn_raw[key] = str(Path(learn_raw[key]).expanduser())

        return cls(
            projects=projects,
            advisors=advisors,
            temporal_host=raw.get("temporal_host", cls.temporal_host),
            task_queue=raw.get("task_queue", cls.task_queue),
            cycle_interval_seconds=raw.get(
                "cycle_interval_seconds", cls.cycle_interval_seconds
            ),
            think_timeout_minutes=raw.get(
                "think_timeout_minutes", cls.think_timeout_minutes
            ),
            build_timeout_minutes=raw.get(
                "build_timeout_minutes", cls.build_timeout_minutes
            ),
            review_timeout_minutes=raw.get(
                "review_timeout_minutes", cls.review_timeout_minutes
            ),
            circuit_breaker=CircuitBreakerConfig(**cb_raw) if cb_raw else CircuitBreakerConfig(),
            learn=LearnConfig(**learn_raw) if learn_raw else LearnConfig(),
            max_cycles_per_day=raw.get("max_cycles_per_day", cls.max_cycles_per_day),
            max_specs_per_cycle=raw.get(
                "max_specs_per_cycle", cls.max_specs_per_cycle
            ),
            max_total_cost_per_day=raw.get(
                "max_total_cost_per_day", cls.max_total_cost_per_day
            ),
        )

    @classmethod
    def default(cls) -> FactoryConfig:
        """Create default config for ClawMarketing + Shell pilot."""
        home = Path.home()
        base = home / "Downloads" / "oyster"

        return cls(
            projects=[
                ProjectConfig(
                    name="clawmarketing",
                    repo_url="https://github.com/nicekid1/clawmarketing.git",
                    repo_local=str(base / "products" / "clawmarketing"),
                    specs_dir=str(base / "specs" / "clawmarketing"),
                ),
                ProjectConfig(
                    name="shell",
                    repo_url="https://github.com/howardleegeek/shell.git",
                    repo_local=str(home / "Downloads" / "shell"),
                    specs_dir=str(base / "specs" / "shell"),
                ),
            ],
            advisors=[
                AdvisorConfig(
                    name="opus",
                    type="opus",
                    model="claude-opus-4-6",
                    api_key_env="ANTHROPIC_API_KEY",
                ),
                AdvisorConfig(
                    name="codex",
                    type="codex",
                    model="o3",
                    api_key_env="OPENAI_API_KEY",
                ),
                AdvisorConfig(
                    name="antigravity",
                    type="antigravity",
                    endpoint=os.environ.get("ANTIGRAVITY_ENDPOINT", ""),
                    api_key_env="ANTIGRAVITY_API_KEY",
                ),
            ],
            learn=LearnConfig(
                trajectory_dir=str(base / "infra" / "dispatch" / "temporal-poc" / "factory" / "trajectories"),
                versioned_prompts_dir=str(base / "infra" / "dispatch" / "temporal-poc" / "factory" / "prompts"),
            ),
        )

    def get_project(self, name: str) -> Optional[ProjectConfig]:
        """Get project config by name."""
        for p in self.projects:
            if p.name == name:
                return p
        return None

    def get_advisor(self, name: str) -> Optional[AdvisorConfig]:
        """Get advisor config by name."""
        for a in self.advisors:
            if a.name == name:
                return a
        return None
