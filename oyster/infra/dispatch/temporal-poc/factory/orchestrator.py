"""
Factory Orchestrator — 24h autonomous loop with 4-phase cycle.

Sources:
- Ralph: Circuit breaker + dual-condition exit (time limit + no progress)
- AutoGen MagenticOne: Progress Ledger self-assessment
- SWE-agent: Batch execution with trajectory logging
- OpenHands: Stuck detection
- Existing: Temporal Schedule for 24h operation

Cycle: Think → Build → Review → Learn → (next cycle)
"""

from __future__ import annotations

import asyncio
import json
import logging
import signal
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .advisors import CLIAdvisor, create_advisors
from .build import BuildResult, SpecDraft, execute_spec, generate_specs_from_consensus
from .circuit_breaker import CircuitBreaker
from .config import FactoryConfig, ProjectConfig
from .learn import EvolutionResult, learn_phase
from .memory import EvolutionMemory
from .review import ReviewVerdict, review_phase
from .think import Consensus, think_phase

logger = logging.getLogger("factory.orchestrator")


@dataclass
class CycleReport:
    """Summary of one Think→Build→Review→Learn cycle."""

    cycle_num: int
    project: str
    started_at: float
    completed_at: float = 0.0

    # Think
    consensus_confidence: float = 0.0
    specs_generated: int = 0

    # Build
    builds_completed: int = 0
    builds_failed: int = 0
    builds_stuck: int = 0

    # Review
    reviews_approved: int = 0
    reviews_rejected: int = 0

    # Learn
    templates_evolved: int = 0
    failure_patterns: int = 0

    # Meta
    made_progress: bool = False
    error: str = ""

    @property
    def duration_seconds(self) -> float:
        return self.completed_at - self.started_at

    def to_dict(self) -> dict:
        return {
            "cycle": self.cycle_num,
            "project": self.project,
            "duration_s": round(self.duration_seconds, 1),
            "consensus_confidence": round(self.consensus_confidence, 3),
            "specs": self.specs_generated,
            "builds": {
                "completed": self.builds_completed,
                "failed": self.builds_failed,
                "stuck": self.builds_stuck,
            },
            "reviews": {
                "approved": self.reviews_approved,
                "rejected": self.reviews_rejected,
            },
            "learn": {
                "evolved": self.templates_evolved,
                "patterns": self.failure_patterns,
            },
            "progress": self.made_progress,
            "error": self.error[:200] if self.error else "",
        }


@dataclass
class FactoryState:
    """Persistent state of the factory across cycles."""

    cycle_count: int = 0
    total_specs_completed: int = 0
    total_specs_failed: int = 0
    started_at: float = 0.0
    last_progress_at: float = 0.0
    cycle_reports: list[dict] = field(default_factory=list)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(
                {
                    "cycle_count": self.cycle_count,
                    "total_specs_completed": self.total_specs_completed,
                    "total_specs_failed": self.total_specs_failed,
                    "started_at": self.started_at,
                    "last_progress_at": self.last_progress_at,
                    "last_10_cycles": self.cycle_reports[-10:],
                },
                f,
                indent=2,
            )

    @classmethod
    def load(cls, path: Path) -> FactoryState:
        if not path.exists():
            return cls()
        try:
            with open(path) as f:
                data = json.load(f)
            return cls(
                cycle_count=data.get("cycle_count", 0),
                total_specs_completed=data.get("total_specs_completed", 0),
                total_specs_failed=data.get("total_specs_failed", 0),
                started_at=data.get("started_at", 0.0),
                last_progress_at=data.get("last_progress_at", 0.0),
                cycle_reports=data.get("last_10_cycles", []),
            )
        except (json.JSONDecodeError, OSError):
            return cls()


class FactoryOrchestrator:
    """Main orchestrator for the Deep Think Factory.

    Runs a continuous loop:
    1. Select next project (round-robin)
    2. Check circuit breaker
    3. Think → Build → Review → Learn
    4. Update circuit breaker
    5. Sleep until next cycle
    """

    def __init__(self, config: FactoryConfig):
        self.config = config
        self._running = False
        self._shutdown_event = asyncio.Event()

        # State directory
        factory_dir = (
            Path.home()
            / "Downloads"
            / "oyster"
            / "infra"
            / "dispatch"
            / "temporal-poc"
            / "factory"
        )
        self._state_dir = factory_dir / "state"
        self._state_dir.mkdir(parents=True, exist_ok=True)

        # Per-project circuit breakers
        self._breakers: dict[str, CircuitBreaker] = {}
        for proj in config.projects:
            self._breakers[proj.name] = CircuitBreaker(
                no_progress_threshold=config.circuit_breaker.no_progress_threshold,
                same_error_threshold=config.circuit_breaker.same_error_threshold,
                cooldown_minutes=config.circuit_breaker.cooldown_minutes,
                auto_reset=config.circuit_breaker.auto_reset,
                state_file=self._state_dir / f"breaker_{proj.name}.json",
            )

        # Shared memory
        self._memory = EvolutionMemory(
            trajectory_dir=config.learn.trajectory_dir
            or str(self._state_dir / "trajectories"),
            prompts_dir=config.learn.versioned_prompts_dir
            or str(self._state_dir / "prompts"),
        )

        # Register default template
        self._memory.register_template("default", "Base spec template")

        # Factory state
        self._state = FactoryState.load(self._state_dir / "factory_state.json")

        # Advisors (created once, reused)
        self._advisors: Optional[list[CLIAdvisor]] = None

    async def start(self, max_hours: float = 24.0) -> None:
        """Start the factory loop.

        Args:
            max_hours: Maximum runtime. Default 24h.
                       Set to 0 for unlimited (until explicit stop).
        """
        self._running = True
        self._state.started_at = time.time()
        deadline = time.time() + max_hours * 3600 if max_hours > 0 else float("inf")

        # Create advisors
        self._advisors = create_advisors()

        logger.info(
            f"[FACTORY] Starting. Projects: {[p.name for p in self.config.projects]}, "
            f"max_hours={max_hours}, cycle_interval={self.config.cycle_interval_seconds}s"
        )

        project_index = 0

        while self._running and time.time() < deadline:
            # Check daily limits
            if self._state.cycle_count >= self.config.max_cycles_per_day:
                logger.info("[FACTORY] Daily cycle limit reached, stopping")
                break

            # Select next project (round-robin)
            project_config = self.config.projects[
                project_index % len(self.config.projects)
            ]
            project_index += 1

            # Check circuit breaker
            breaker = self._breakers[project_config.name]
            allowed, reason = breaker.should_allow_cycle()

            if not allowed:
                logger.info(
                    f"[FACTORY] Circuit breaker OPEN for {project_config.name}: {reason}"
                )
                await self._sleep_or_shutdown(self.config.cycle_interval_seconds)
                continue

            # Run one cycle
            try:
                report = await self._run_cycle(
                    project_config, self._state.cycle_count + 1
                )
            except Exception as e:
                logger.error(f"[FACTORY] Cycle error for {project_config.name}: {e}")
                report = CycleReport(
                    cycle_num=self._state.cycle_count + 1,
                    project=project_config.name,
                    started_at=time.time(),
                    completed_at=time.time(),
                    error=str(e),
                )

            # Update state
            self._state.cycle_count += 1
            self._state.total_specs_completed += report.builds_completed
            self._state.total_specs_failed += report.builds_failed + report.builds_stuck
            self._state.cycle_reports.append(report.to_dict())

            # Emit cycle event to AI OS global log
            _emit_ai_os_cycle_event(report)

            # Update circuit breaker
            if report.made_progress:
                breaker.record_progress(self._state.cycle_count)
                self._state.last_progress_at = time.time()
            else:
                breaker.record_no_progress(self._state.cycle_count, report.error)

            # Persist state
            self._state.save(self._state_dir / "factory_state.json")

            logger.info(
                f"[FACTORY] Cycle {self._state.cycle_count} done: "
                f"{project_config.name} "
                f"completed={report.builds_completed} "
                f"failed={report.builds_failed} "
                f"progress={report.made_progress} "
                f"duration={report.duration_seconds:.0f}s"
            )

            # Sleep between cycles
            await self._sleep_or_shutdown(self.config.cycle_interval_seconds)

        self._running = False
        logger.info(
            f"[FACTORY] Stopped. Total cycles={self._state.cycle_count}, "
            f"completed={self._state.total_specs_completed}, "
            f"failed={self._state.total_specs_failed}"
        )

    async def stop(self) -> None:
        """Gracefully stop the factory."""
        logger.info("[FACTORY] Stop requested")
        self._running = False
        self._shutdown_event.set()

    async def _run_cycle(self, project: ProjectConfig, cycle_num: int) -> CycleReport:
        """Run one Think→Build→Review→Learn cycle for a project."""
        report = CycleReport(
            cycle_num=cycle_num,
            project=project.name,
            started_at=time.time(),
        )

        # ── Phase 1: Think ──
        logger.info(f"[CYCLE {cycle_num}] Phase 1: THINK ({project.name})")
        try:
            consensus = await asyncio.wait_for(
                think_phase(
                    project=project.name,
                    project_dir=project.repo_local,
                    memory=self._memory,
                    advisors=self._advisors,
                ),
                timeout=self.config.think_timeout_minutes * 60,
            )
        except asyncio.TimeoutError:
            report.error = "Think phase timed out"
            report.completed_at = time.time()
            return report
        except Exception as e:
            report.error = f"Think phase error: {e}"
            report.completed_at = time.time()
            return report

        report.consensus_confidence = consensus.confidence

        if not consensus.should_proceed:
            logger.info(
                f"[CYCLE {cycle_num}] Think phase: low confidence "
                f"({consensus.confidence:.2f}), skipping build"
            )
            report.completed_at = time.time()
            return report

        # ── Phase 2: Build ──
        logger.info(f"[CYCLE {cycle_num}] Phase 2: BUILD ({project.name})")
        specs = generate_specs_from_consensus(
            consensus,
            project=project.name,
            specs_dir=project.specs_dir,
            memory=self._memory,
            max_specs=self.config.max_specs_per_cycle,
        )
        report.specs_generated = len(specs)

        if not specs:
            logger.info(f"[CYCLE {cycle_num}] No specs generated, skipping build")
            report.completed_at = time.time()
            return report

        # Execute specs sequentially (respects depends_on ordering)
        build_results: list[BuildResult] = []
        for spec in specs:
            spec.max_reflections = project.max_reflections
            try:
                result = await asyncio.wait_for(
                    execute_spec(
                        spec,
                        project_dir=project.repo_local,
                        memory=self._memory,
                    ),
                    timeout=self.config.build_timeout_minutes * 60,
                )
            except asyncio.TimeoutError:
                result = BuildResult(
                    task_id=spec.task_id,
                    project=spec.project,
                    status="failed",
                    error="Build timed out",
                )
            except Exception as e:
                result = BuildResult(
                    task_id=spec.task_id,
                    project=spec.project,
                    status="failed",
                    error=str(e),
                )

            build_results.append(result)

            if result.status == "completed":
                report.builds_completed += 1
            elif result.status == "stuck":
                report.builds_stuck += 1
            else:
                report.builds_failed += 1

        # ── Phase 3: Review ──
        logger.info(f"[CYCLE {cycle_num}] Phase 3: REVIEW ({project.name})")
        review_verdicts: list[ReviewVerdict] = []
        for br in build_results:
            if br.status != "completed":
                continue
            try:
                verdict = await asyncio.wait_for(
                    review_phase(
                        br,
                        spec_content=_get_spec_content(br, specs),
                        advisors=self._advisors,
                    ),
                    timeout=self.config.review_timeout_minutes * 60,
                )
            except asyncio.TimeoutError:
                verdict = ReviewVerdict(
                    status="reject",
                    issues=["Review timed out"],
                )
            except Exception as e:
                verdict = ReviewVerdict(
                    status="reject",
                    issues=[f"Review error: {e}"],
                )

            review_verdicts.append(verdict)

            if verdict.should_merge:
                report.reviews_approved += 1
            else:
                report.reviews_rejected += 1

        # ── Phase 4: Learn ──
        logger.info(f"[CYCLE {cycle_num}] Phase 4: LEARN ({project.name})")
        evolve_this_cycle = (
            self.config.learn.enabled
            and cycle_num % self.config.learn.evolve_every_n_cycles == 0
        )

        try:
            evolution = await learn_phase(
                build_results=build_results,
                review_verdicts=review_verdicts,
                project=project.name,
                memory=self._memory,
                advisors=self._advisors,
                evolve_this_cycle=evolve_this_cycle,
            )
            report.templates_evolved = evolution.templates_mutated
            report.failure_patterns = evolution.failure_patterns_found
        except Exception as e:
            logger.error(f"[CYCLE {cycle_num}] Learn error: {e}")

        # Determine if we made progress — requires actual code output, not just exit 0
        total_loc = sum(br.loc_added for br in build_results)
        report.made_progress = (
            report.builds_completed > 0
            and report.reviews_approved > 0
            and total_loc > 0
        )
        report.completed_at = time.time()

        return report

    async def _sleep_or_shutdown(self, seconds: float) -> None:
        """Sleep for `seconds` unless shutdown is requested."""
        try:
            await asyncio.wait_for(self._shutdown_event.wait(), timeout=seconds)
        except asyncio.TimeoutError:
            pass  # Normal — timeout means sleep completed

    @property
    def state(self) -> FactoryState:
        return self._state

    @property
    def is_running(self) -> bool:
        return self._running


def _get_spec_content(build_result: BuildResult, specs: list[SpecDraft]) -> str:
    """Find the spec content that produced this build result."""
    for spec in specs:
        if spec.task_id == build_result.task_id:
            return spec.content
    return ""


def _emit_ai_os_cycle_event(report: CycleReport) -> None:
    """Emit a compliant NDJSON event to AI OS global events log upon cycle completion."""
    from datetime import datetime

    try:
        now = datetime.utcnow()
        month_str = now.strftime("%Y-%m")
        event_file = (
            Path.home()
            / "Downloads"
            / "oyster"
            / "infra"
            / "infrastructure"
            / "ai_os"
            / "events"
            / f"{month_str}.ndjson"
        )
        event_file.parent.mkdir(parents=True, exist_ok=True)

        event = {
            "ts": now.isoformat() + "Z",
            "actor": "factory-orchestrator",
            "type": "factory.cycle_completed",
            "project": report.project,
            "metrics": {
                "cycle": report.cycle_num,
                "duration_s": round(report.duration_seconds, 1),
                "builds_completed": report.builds_completed,
                "builds_failed": report.builds_failed,
                "made_progress": report.made_progress,
            },
        }
        with open(event_file, "a") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        logger.warning(f"Failed to append to AI OS event log: {e}")


async def run_factory(
    config: Optional[FactoryConfig] = None,
    config_path: Optional[str] = None,
    max_hours: float = 24.0,
) -> None:
    """Entry point: load config and run the factory.

    Usage:
        # With default config
        asyncio.run(run_factory())

        # With custom YAML config
        asyncio.run(run_factory(config_path="factory.yaml"))

        # With programmatic config
        asyncio.run(run_factory(config=my_config))
    """
    if config is None:
        if config_path:
            config = FactoryConfig.from_yaml(config_path)
        else:
            config = FactoryConfig.default()

    orchestrator = FactoryOrchestrator(config)

    # Handle graceful shutdown on SIGINT/SIGTERM
    loop = asyncio.get_running_loop()

    def _handle_signal() -> None:
        logger.info("[FACTORY] Signal received, shutting down...")
        asyncio.ensure_future(orchestrator.stop())

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _handle_signal)

    await orchestrator.start(max_hours=max_hours)
