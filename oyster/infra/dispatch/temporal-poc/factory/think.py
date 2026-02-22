"""
Think Phase — Multi-advisor consensus before spec generation.

Sources:
- AutoGen MagenticOne: Dual ledger (Task Ledger + Progress Ledger)
- EvoAgentX: WorkFlowGenerator pattern
- Multi-advisor parallel independent thinking (anti-anchoring)
"""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .advisors import (
    AdvisorOpinion,
    CLIAdvisor,
    create_advisors,
    gather_opinions,
)
from .memory import EvolutionMemory

logger = logging.getLogger("factory.think")


@dataclass
class TaskLedger:
    """MagenticOne Task Ledger — what we know and what we plan."""

    project: str
    codebase_summary: str
    known_facts: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    plan: list[str] = field(default_factory=list)
    direction: str = ""


@dataclass
class ProgressLedger:
    """MagenticOne Progress Ledger — are we making progress?"""

    last_cycle_outcome: str = ""
    tasks_completed_recently: int = 0
    tasks_failed_recently: int = 0
    stall_count: int = 0
    is_making_progress: bool = True


@dataclass
class Consensus:
    """Synthesized consensus from multi-advisor thinking."""

    agreed_points: list[str]  # all advisors agree
    single_advisor_insights: list[str]  # only one advisor raised this
    disagreements: list[str]  # advisors disagree
    blind_spots: list[str]  # nobody mentioned but should consider
    recommended_specs: list[dict]  # spec outlines to generate
    confidence: float  # overall confidence
    raw_opinions: list[AdvisorOpinion] = field(default_factory=list)

    @property
    def should_proceed(self) -> bool:
        """Should we proceed to Build phase?"""
        return (
            self.confidence >= 0.5
            and len(self.recommended_specs) > 0
        )


def scan_codebase(project_dir: str) -> str:
    """Generate a concise codebase summary (Aider repo-map style)."""
    project_path = Path(project_dir)
    if not project_path.exists():
        return f"Project directory not found: {project_dir}"

    lines = [f"# Codebase Summary: {project_path.name}\n"]

    # File tree (top-level only, exclude common noise)
    exclude = {
        ".git", "node_modules", "__pycache__", ".next",
        "venv", ".venv", "dist", "build", ".cache",
    }
    try:
        entries = sorted(project_path.iterdir())
        for entry in entries:
            if entry.name in exclude or entry.name.startswith("."):
                continue
            if entry.is_dir():
                sub_count = sum(1 for _ in entry.rglob("*") if _.is_file())
                lines.append(f"  {entry.name}/ ({sub_count} files)")
            else:
                size_kb = entry.stat().st_size // 1024
                lines.append(f"  {entry.name} ({size_kb}KB)")
    except OSError:
        lines.append("  (unable to list directory)")

    # Recent git log
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-10"],
            cwd=str(project_path),
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            lines.append("\n## Recent commits")
            lines.append(result.stdout.strip())
    except (subprocess.TimeoutExpired, OSError):
        pass

    # Key files content summary
    key_files = ["README.md", "package.json", "pyproject.toml", "requirements.txt"]
    for kf in key_files:
        kf_path = project_path / kf
        if kf_path.exists():
            try:
                content = kf_path.read_text()[:500]
                lines.append(f"\n## {kf} (first 500 chars)")
                lines.append(content)
            except OSError:
                pass

    return "\n".join(lines)[:4000]  # cap at 4K chars


def build_task_ledger(
    project: str,
    project_dir: str,
    direction: str = "",
    memory: Optional[EvolutionMemory] = None,
) -> TaskLedger:
    """Build the MagenticOne Task Ledger for a project."""
    codebase_summary = scan_codebase(project_dir)

    known_facts = []
    open_questions = []

    # Add failure patterns from memory
    if memory:
        failures = memory.get_failure_patterns(project, limit=5)
        if failures:
            known_facts.append(
                f"Recent failures ({len(failures)}): "
                + ", ".join(f.get("failure_reason", "unknown")[:50] for f in failures[:3])
            )

        # Template stats
        stats = memory.get_template_stats()
        if stats:
            best = stats[0]
            known_facts.append(
                f"Best template: {best['template_id']} "
                f"(CMP={best['cmp']}, {best['successes']}/{best['successes']+best['failures']})"
            )

    return TaskLedger(
        project=project,
        codebase_summary=codebase_summary,
        known_facts=known_facts,
        open_questions=open_questions,
        direction=direction,
    )


def build_progress_ledger(
    project: str,
    memory: Optional[EvolutionMemory] = None,
) -> ProgressLedger:
    """Build the MagenticOne Progress Ledger."""
    if not memory:
        return ProgressLedger()

    recent = memory.load_trajectories(project, limit=10)
    completed = sum(1 for t in recent if t.get("outcome") == "success")
    failed = sum(1 for t in recent if t.get("outcome") == "failed")

    # Detect stall: if last 3 cycles all failed
    last_3 = recent[:3]
    stall = sum(1 for t in last_3 if t.get("outcome") == "failed")

    return ProgressLedger(
        tasks_completed_recently=completed,
        tasks_failed_recently=failed,
        stall_count=stall,
        is_making_progress=stall < 3,
    )


def _codebase_driven_fallback(
    task_ledger: TaskLedger,
    raw_opinions: list[AdvisorOpinion],
) -> Consensus:
    """Zero-advisor fallback: derive specs from codebase analysis alone.

    When all advisors fail (API quotas exhausted), we still produce
    actionable specs by analyzing the codebase structure.
    """
    logger.warning("[THINK] All advisors failed — using codebase-driven fallback")

    specs = []
    summary = task_ledger.codebase_summary.lower()

    # Heuristic: look for common improvement opportunities
    if "test" not in summary and "spec" not in summary:
        specs.append({
            "direction": "Add basic test coverage for core modules",
            "source": "codebase_fallback",
            "priority": 1,
        })

    if "readme" not in summary:
        specs.append({
            "direction": "Create or update README with setup instructions",
            "source": "codebase_fallback",
            "priority": 2,
        })

    # Check for TODO/FIXME in known_facts
    for fact in task_ledger.known_facts:
        if "fail" in fact.lower():
            specs.append({
                "direction": f"Fix recurring issue: {fact[:80]}",
                "source": "codebase_fallback",
                "priority": 1,
            })

    # If direction was given, use it directly
    if task_ledger.direction:
        specs.insert(0, {
            "direction": task_ledger.direction,
            "source": "user_direction",
            "priority": 1,
        })

    # Always produce at least one spec
    if not specs:
        specs.append({
            "direction": "Review and improve code quality in the most recently modified files",
            "source": "codebase_fallback",
            "priority": 2,
        })

    return Consensus(
        agreed_points=[],
        single_advisor_insights=[],
        disagreements=[],
        blind_spots=["No advisors available — using codebase heuristics only"],
        recommended_specs=specs[:5],
        confidence=0.55,  # just above should_proceed threshold
        raw_opinions=raw_opinions,
    )


async def synthesize_consensus(
    opinions: list[AdvisorOpinion],
    task_ledger: TaskLedger,
) -> Consensus:
    """Synthesize multi-advisor opinions into consensus.

    Not a vote — finds agreement, unique insights, and blind spots.
    """
    valid_opinions = [o for o in opinions if o.is_valid]

    if not valid_opinions:
        # Zero-advisor fallback: derive specs from codebase analysis
        return _codebase_driven_fallback(task_ledger, opinions)

    # Collect all recommendations
    all_recs: dict[str, list[str]] = {}  # advisor → recs
    all_risks: dict[str, list[str]] = {}

    for op in valid_opinions:
        all_recs[op.advisor_name] = op.recommendations
        all_risks[op.advisor_name] = op.risks

    # Find agreement: recommendations mentioned by 2+ advisors
    all_rec_texts = []
    for recs in all_recs.values():
        all_rec_texts.extend(recs)

    # Simple overlap detection (exact match for now, could use embeddings)
    rec_counts: dict[str, int] = {}
    for r in all_rec_texts:
        # Handle both string and dict recommendations
        if isinstance(r, dict):
            r = r.get("text", r.get("description", str(r)))
        r = str(r)
        key = r.lower().strip()[:80]
        rec_counts[key] = rec_counts.get(key, 0) + 1

    agreed = [r for r, c in rec_counts.items() if c >= 2]
    single = [r for r, c in rec_counts.items() if c == 1]

    # All risks are worth noting
    all_risk_texts = []
    for risks in all_risks.values():
        for r in risks:
            if isinstance(r, dict):
                r = r.get("text", r.get("description", str(r)))
            all_risk_texts.append(str(r))

    # Average confidence
    avg_conf = sum(o.confidence for o in valid_opinions) / len(valid_opinions)

    # Generate spec outlines from agreed recommendations
    recommended_specs = []
    for rec in (agreed or single[:3]):  # if no agreement, use top single insights
        recommended_specs.append({
            "direction": rec,
            "source": "consensus" if rec in agreed else "single_advisor",
            "priority": 1 if rec in agreed else 2,
        })

    # Fallback: if advisors responded but had no structured recs,
    # extract direction from their analysis text
    if not recommended_specs and valid_opinions:
        for op in valid_opinions:
            if op.analysis and len(op.analysis) > 20:
                # Use first sentence of analysis as direction
                first_sentence = op.analysis.split(".")[0].strip()[:100]
                if first_sentence:
                    recommended_specs.append({
                        "direction": first_sentence,
                        "source": f"analysis_{op.advisor_name}",
                        "priority": 2,
                    })
                    break

    # Ultimate fallback: codebase-driven if still empty
    if not recommended_specs:
        fallback = _codebase_driven_fallback(task_ledger, opinions)
        return fallback

    return Consensus(
        agreed_points=agreed,
        single_advisor_insights=single[:5],
        disagreements=[],  # TODO: detect contradictions
        blind_spots=all_risk_texts[:5],
        recommended_specs=recommended_specs[:5],  # cap at 5
        confidence=avg_conf,
        raw_opinions=opinions,
    )


async def think_phase(
    project: str,
    project_dir: str,
    direction: str = "",
    memory: Optional[EvolutionMemory] = None,
    advisors: Optional[list[CLIAdvisor]] = None,
) -> Consensus:
    """
    Run the full Think Phase:
    1. Build Task Ledger (codebase scan + memory)
    2. Build Progress Ledger
    3. Gather independent advisor opinions (parallel)
    4. Synthesize consensus
    """
    logger.info(f"[THINK] Starting for {project}")

    # 1. Task Ledger
    task_ledger = build_task_ledger(project, project_dir, direction, memory)
    logger.info(f"[THINK] Task Ledger: {len(task_ledger.known_facts)} facts")

    # 2. Progress Ledger
    progress_ledger = build_progress_ledger(project, memory)
    if not progress_ledger.is_making_progress:
        logger.warning(f"[THINK] Stall detected! {progress_ledger.stall_count} consecutive failures")

    # 3. Gather opinions (parallel — anti-anchoring)
    if advisors is None:
        advisors = create_advisors()

    question = direction or (
        f"What should be the next development priority for {project}? "
        f"Consider: existing codebase state, recent failures, and strategic direction."
    )

    context = (
        f"Project: {project}\n"
        f"Direction: {direction or 'autonomous discovery'}\n"
        f"Known facts: {json.dumps(task_ledger.known_facts)}\n"
        f"Recent progress: completed={progress_ledger.tasks_completed_recently}, "
        f"failed={progress_ledger.tasks_failed_recently}\n"
        f"Stall count: {progress_ledger.stall_count}"
    )

    logger.info(f"[THINK] Gathering {len(advisors)} advisor opinions in parallel...")
    opinions = await gather_opinions(
        advisors, context, question, task_ledger.codebase_summary
    )

    valid_count = sum(1 for o in opinions if o.is_valid)
    logger.info(f"[THINK] Got {valid_count}/{len(opinions)} valid opinions")

    # 4. Synthesize
    consensus = await synthesize_consensus(opinions, task_ledger)
    logger.info(
        f"[THINK] Consensus: {len(consensus.agreed_points)} agreed, "
        f"{len(consensus.recommended_specs)} specs, "
        f"confidence={consensus.confidence:.2f}, "
        f"proceed={consensus.should_proceed}"
    )

    return consensus
