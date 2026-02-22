"""
Build Phase — Spec generation and bounded execution.

Sources:
- Aider: Bounded reflection loop (max_reflections=3)
- Aider: Architect/Editor dual-model split
- SWE-agent: YAML config, trajectory logging, batch execution
- Existing: task-wrapper.sh (kept as-is)

Note: All subprocess calls use asyncio.create_subprocess_exec with explicit
argument lists (no shell=True) to prevent command injection.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .memory import EvolutionMemory, TaskTrajectory, TrajectoryStep
from .stuck_detector import StepRecord, StuckDetector
from .think import Consensus

logger = logging.getLogger("factory.build")


@dataclass
class SpecDraft:
    """A spec ready for execution."""

    task_id: str
    project: str
    content: str
    template_id: str = "default"
    depends_on: list[str] = field(default_factory=list)
    estimated_minutes: int = 30
    max_reflections: int = 3  # Aider pattern
    advisor_context: str = ""  # injected from Think phase


@dataclass
class BuildResult:
    """Result of executing a spec."""

    task_id: str
    project: str
    status: str  # "completed" | "failed" | "stuck" | "needs_human"
    diff: str = ""
    test_output: str = ""
    error: str = ""
    duration_seconds: float = 0.0
    reflections_used: int = 0
    loc_added: int = 0  # Actual lines of code produced (0 = empty run)
    trajectory: Optional[TaskTrajectory] = None


def generate_specs_from_consensus(
    consensus: Consensus,
    project: str,
    specs_dir: str,
    memory: Optional[EvolutionMemory] = None,
    max_specs: int = 5,
) -> list[SpecDraft]:
    """Generate atomic spec files from Think phase consensus."""
    specs = []
    specs_path = Path(specs_dir)
    specs_path.mkdir(parents=True, exist_ok=True)

    # Select template using Thompson Sampling if available
    template_id = "default"
    if memory:
        selected = memory.select_best_template()
        if selected:
            template_id = selected

    spec_template = _get_spec_template(template_id, memory)

    for i, rec in enumerate(consensus.recommended_specs[:max_specs]):
        task_id = f"S{i + 1:02d}-{_slugify(rec['direction'][:30])}"

        advisor_context = ""
        if consensus.agreed_points:
            advisor_context += "## Advisor Consensus\n"
            for ap in consensus.agreed_points[:3]:
                advisor_context += f"- {ap}\n"
        if consensus.blind_spots:
            advisor_context += "\n## Identified Risks\n"
            for bs in consensus.blind_spots[:3]:
                advisor_context += f"- {bs}\n"

        content = spec_template.format(
            task_id=task_id,
            project=project,
            direction=rec["direction"],
            priority=rec.get("priority", 1),
            advisor_context=advisor_context,
        )

        spec = SpecDraft(
            task_id=task_id,
            project=project,
            content=content,
            template_id=template_id,
            estimated_minutes=30,
            advisor_context=advisor_context,
        )
        specs.append(spec)

        spec_file = specs_path / f"{task_id}.md"
        spec_file.write_text(content)
        logger.info(f"[BUILD] Generated spec: {task_id}")

    return specs


def _get_spec_template(
    template_id: str, memory: Optional[EvolutionMemory] = None
) -> str:
    """Get the spec template (from memory or default)."""
    if memory:
        stored = memory.get_current_prompt(template_id)
        if stored:
            return stored

    return """---
task_id: {task_id}
project: {project}
priority: {priority}
estimated_minutes: 30
depends_on: []
---
## Goal
{direction}

{advisor_context}

## Constraints
- Work within the existing codebase structure
- Write meaningful tests for new functionality
- Do not refactor unrelated code
- Do not change UI/CSS unless explicitly required

## Acceptance Criteria
- [ ] Core functionality implemented
- [ ] Tests pass
- [ ] No lint errors
- [ ] Changes are minimal and focused

## Do NOT
- Restructure the project layout
- Add unnecessary dependencies
- Over-engineer the solution
"""


def _slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text)
    return text[:30].strip("-")


async def execute_spec(
    spec: SpecDraft,
    project_dir: str,
    memory: Optional[EvolutionMemory] = None,
) -> BuildResult:
    """Execute a single spec with bounded reflection (Aider pattern).

    Loop:
    1. Run task-wrapper.sh
    2. Check result
    3. If failed and reflections < max: analyze error, retry
    4. If stuck (StuckDetector): abort
    """
    start_time = time.time()
    trajectory = TaskTrajectory(
        task_id=spec.task_id,
        project=spec.project,
        spec_content=spec.content,
        template_id=spec.template_id,
        started_at=start_time,
    )

    detector = StuckDetector()
    last_error = ""
    consecutive_zero_loc = 0  # Size diff early kill counter

    for reflection in range(spec.max_reflections + 1):
        step_start = time.time()
        logger.info(
            f"[BUILD] {spec.task_id} attempt {reflection + 1}/{spec.max_reflections + 1}"
        )

        spec_content = spec.content
        if reflection > 0 and last_error:
            spec_content += (
                f"\n\n## Previous Attempt Failed\n{last_error}\n\nFix the issue above."
            )

        result = await _run_task_wrapper(
            spec.task_id, spec.project, spec_content, project_dir
        )

        step_duration = time.time() - step_start
        loc_added = result.get("loc_added", 0)

        trajectory.add_step(
            TrajectoryStep(
                timestamp=time.time(),
                phase="build",
                action=f"execute_attempt_{reflection + 1}",
                result=result["status"],
                duration_seconds=step_duration,
                error=result.get("error", ""),
            )
        )

        detector.add_step(
            StepRecord(
                step_num=reflection,
                action=f"run_{spec.task_id}",
                observation=f"loc_added={loc_added} | {result.get('output', '')[:150]}",
                is_error=result["status"] != "completed",
            )
        )

        # Size diff early kill: 2 consecutive +0 runs = abort
        if loc_added == 0:
            consecutive_zero_loc += 1
            if consecutive_zero_loc >= 2:
                logger.warning(
                    f"[BUILD] {spec.task_id}: 2 consecutive runs with loc_added=0 — early kill"
                )
                trajectory.outcome = "stuck"
                trajectory.failure_reason = "size_diff_early_kill: 2x loc_added=0"
                trajectory.completed_at = time.time()
                if memory:
                    memory.save_trajectory(trajectory)
                    memory.record_template_outcome(spec.template_id, success=False)
                return BuildResult(
                    task_id=spec.task_id,
                    project=spec.project,
                    status="stuck",
                    error="Early kill: 2 consecutive attempts produced 0 lines of code",
                    duration_seconds=time.time() - start_time,
                    reflections_used=reflection + 1,
                    loc_added=0,
                    trajectory=trajectory,
                )
        else:
            consecutive_zero_loc = 0  # Reset counter on any real output

        stuck = detector.check()
        if stuck and stuck.severity >= 2:
            logger.warning(f"[BUILD] {spec.task_id} stuck: {stuck.pattern_name}")
            trajectory.outcome = "stuck"
            trajectory.failure_reason = f"stuck:{stuck.pattern_name}"
            trajectory.completed_at = time.time()
            if memory:
                memory.save_trajectory(trajectory)
                memory.record_template_outcome(spec.template_id, success=False)
            return BuildResult(
                task_id=spec.task_id,
                project=spec.project,
                status="stuck",
                error=f"Stuck: {stuck.pattern_name} -- {stuck.evidence}",
                duration_seconds=time.time() - start_time,
                reflections_used=reflection + 1,
                loc_added=loc_added,
                trajectory=trajectory,
            )

        if result["status"] == "completed":
            trajectory.outcome = "success"
            trajectory.completed_at = time.time()
            if memory:
                memory.save_trajectory(trajectory)
                memory.record_template_outcome(spec.template_id, success=True)
            return BuildResult(
                task_id=spec.task_id,
                project=spec.project,
                status="completed",
                diff=result.get("diff", ""),
                test_output=result.get("output", ""),
                duration_seconds=time.time() - start_time,
                reflections_used=reflection + 1,
                loc_added=loc_added,
                trajectory=trajectory,
            )

        last_error = result.get("error", "") or result.get("output", "")[-500:]
        logger.info(
            f"[BUILD] {spec.task_id} failed (loc_added={loc_added}), will retry. Error: {last_error[:100]}..."
        )

    # Exhausted all reflections
    trajectory.outcome = "failed"
    trajectory.failure_reason = last_error[:500]
    trajectory.completed_at = time.time()
    if memory:
        memory.save_trajectory(trajectory)
        memory.record_template_outcome(spec.template_id, success=False)

    return BuildResult(
        task_id=spec.task_id,
        project=spec.project,
        status="failed",
        error=f"Failed after {spec.max_reflections + 1} attempts: {last_error[:300]}",
        duration_seconds=time.time() - start_time,
        reflections_used=spec.max_reflections + 1,
        trajectory=trajectory,
    )


def _read_loc_added(task_dir: Path) -> int:
    """Read loc_added from status.json, or check result files for evidence of output."""
    status_file = task_dir / "status.json"
    if status_file.exists():
        try:
            with open(status_file) as f:
                data = json.load(f)
            loc = data.get("loc_added", data.get("LOC_ADDED", 0))
            if isinstance(loc, int) and loc > 0:
                return loc
        except (json.JSONDecodeError, OSError):
            pass

    # Fallback: check progress.txt / result.txt for any diff info
    for fname in ("result.txt", "progress.txt"):
        result_file = task_dir / fname
        if result_file.exists():
            try:
                content = result_file.read_text()
                if "files_modified" in content and content.strip():
                    return 1  # At least something was produced
            except OSError:
                pass

    return 0


def _determine_model_tier(spec_content: str) -> str:
    """Dynamically determine the model tier based on task complexity.
    Heavy Tier: architectural, complex, or investigation tasks.
    Light Tier: standard code edits, tests, types, config.
    """
    content_lower = spec_content.lower()
    heavy_signals = [
        "audit",
        "investigate",
        "architect",
        "redesign",
        "refactor",
        "complex",
        "root cause",
        "security",
        "bottleneck",
        "re-architect",
        "system",
        "infrastructure",
        "evaluation",
    ]
    for signal in heavy_signals:
        if signal in content_lower:
            return "opencode/minimax-m2.5-free,opencode/trinity-large-preview-free"

    # Default to fast, lightweight models to save cost and increase throughput
    return "opencode/glm-5-free,opencode/gpt-5-nano"


async def _run_task_wrapper(
    task_id: str,
    project: str,
    spec_content: str,
    project_dir: str,
) -> dict:
    """Run task-wrapper.sh and check actual code output via loc_added.

    Exit code 0 with loc_added == 0 is treated as empty_run (not completed).
    Uses create_subprocess_exec with explicit arg list (no shell injection).
    """
    temporal_dir = (
        Path.home() / "Downloads" / "oyster" / "infra" / "dispatch" / "temporal-poc"
    )
    wrapper = temporal_dir / "task-wrapper.sh"

    if not wrapper.exists():
        return {
            "status": "failed",
            "error": f"task-wrapper.sh not found at {wrapper}",
            "output": "",
            "loc_added": 0,
        }

    task_dir = temporal_dir / project / "tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    spec_file = task_dir / "spec.md"
    spec_file.write_text(spec_content)

    env = {
        **os.environ,
        "TASK_ID": task_id,
        "PROJECT": project,
        "SPEC_FILE": str(spec_file),
        "WORKING_DIR": project_dir,
        "TASK_DIR": str(task_dir),
        "LOG_FILE": str(task_dir / "task.log"),
        "ESTIMATED_MINUTES": "30",
        "API_MODE": "opencode",
        "OPENCODE_MODELS": _determine_model_tier(spec_content),
        "CI": "1",
        "PAGER": "cat",
        "GIT_PAGER": "cat",
    }
    env.pop("CLAUDECODE", None)

    timeout_secs = 30 * 60 * 3

    try:
        proc = await asyncio.create_subprocess_exec(
            "bash",
            str(wrapper),
            project,
            task_id,
            str(spec_file),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=project_dir,
            env=env,
        )
        stdout_bytes, _ = await asyncio.wait_for(
            proc.communicate(), timeout=timeout_secs
        )
        output = stdout_bytes.decode("utf-8", errors="replace")[-2000:]
        output = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", output)
        output = re.sub(r"[\x00-\x08\x0e-\x1f]", "", output)

        with open(task_dir / "task.log", "a") as f:
            f.write(output)

        loc_added = _read_loc_added(task_dir)

        if proc.returncode == 0:
            if loc_added == 0:
                logger.warning(f"[BUILD] {task_id}: exit 0 but loc_added=0 — empty_run")
                return {
                    "status": "failed",
                    "output": output,
                    "error": "Empty run: exit 0 but loc_added=0, no code produced",
                    "diff": "",
                    "loc_added": 0,
                }
            return {
                "status": "completed",
                "output": output,
                "diff": "",
                "error": "",
                "loc_added": loc_added,
            }

        return {
            "status": "failed",
            "output": output,
            "error": f"Exit code {proc.returncode}",
            "diff": "",
            "loc_added": loc_added,
        }

    except asyncio.TimeoutError:
        return {
            "status": "failed",
            "error": f"Timeout after {timeout_secs}s",
            "output": "",
            "diff": "",
            "loc_added": 0,
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "output": "",
            "diff": "",
            "loc_added": 0,
        }
