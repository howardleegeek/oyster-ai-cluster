"""
Learn Phase — GEPA-style prompt evolution + trajectory analysis.

Sources:
- OpenAI GEPA: Genetic-Pareto evolutionary prompt optimization
- HGM: Thompson Sampling updates + CMP re-scoring
- SWE-agent: Trajectory JSONL → failure pattern mining
- Aider: Bounded evolution (max 3 mutations per cycle)

The Learn Phase runs after Review and feeds improvements back into Think:
1. Analyze trajectories → extract failure patterns
2. Evolve spec templates (mutate, crossover, prune)
3. Update Thompson Sampling stats
4. Persist new prompt versions
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass, field
from typing import Optional

from .advisors import CLIAdvisor, create_advisors
from .build import BuildResult
from .memory import EvolutionMemory, PromptVersion
from .review import ReviewVerdict

logger = logging.getLogger("factory.learn")


@dataclass
class FailurePattern:
    """Extracted pattern from repeated failures."""

    pattern_type: str  # "timeout" | "lint" | "test" | "stuck" | "compile"
    frequency: int  # how many times seen
    example_error: str  # representative error text
    affected_projects: list[str] = field(default_factory=list)
    suggested_fix: str = ""


@dataclass
class EvolutionResult:
    """Result of one evolution cycle."""

    templates_mutated: int = 0
    templates_pruned: int = 0
    failure_patterns_found: int = 0
    prompt_versions_created: int = 0
    thompson_updates: int = 0


def extract_failure_patterns(
    trajectories: list[dict],
    min_frequency: int = 2,
) -> list[FailurePattern]:
    """Mine failure patterns from trajectory history (SWE-agent pattern).

    Groups failures by error signature to find recurring problems.
    """
    error_buckets: dict[str, list[dict]] = {}

    for traj in trajectories:
        if traj.get("outcome") != "failed":
            continue

        reason = traj.get("failure_reason", "unknown")
        error_key = _classify_error(reason)
        if error_key not in error_buckets:
            error_buckets[error_key] = []
        error_buckets[error_key].append(traj)

    patterns = []
    for error_key, trajs in error_buckets.items():
        if len(trajs) < min_frequency:
            continue

        projects = list({t.get("project", "?") for t in trajs})
        example = trajs[0].get("failure_reason", "")[:300]

        patterns.append(FailurePattern(
            pattern_type=error_key,
            frequency=len(trajs),
            example_error=example,
            affected_projects=projects,
            suggested_fix=_suggest_fix(error_key, example),
        ))

    patterns.sort(key=lambda p: p.frequency, reverse=True)
    return patterns


def _classify_error(error_text: str) -> str:
    """Classify an error into a bucket."""
    lower = error_text.lower()

    if "timeout" in lower or "timed out" in lower:
        return "timeout"
    if "lint" in lower or "eslint" in lower or "black" in lower:
        return "lint"
    if "test" in lower and ("fail" in lower or "error" in lower):
        return "test"
    if "stuck" in lower or "loop" in lower:
        return "stuck"
    if "compile" in lower or "syntax" in lower or "import" in lower:
        return "compile"
    if "permission" in lower or "access denied" in lower:
        return "permission"
    if "not found" in lower or "no such file" in lower:
        return "missing_file"
    return "unknown"


def _suggest_fix(error_type: str, example: str) -> str:
    """Generate a simple fix suggestion based on error type."""
    suggestions = {
        "timeout": "Reduce spec scope or increase estimated_minutes",
        "lint": "Add explicit lint rules to spec constraints section",
        "test": "Add specific test expectations to acceptance criteria",
        "stuck": "Simplify the spec direction or add more concrete steps",
        "compile": "Add imports/dependencies to spec constraints",
        "permission": "Check file permissions and working directory",
        "missing_file": "Verify file paths exist before referencing",
        "unknown": "Review error details and add constraints to prevent recurrence",
    }
    return suggestions.get(error_type, suggestions["unknown"])


async def evolve_templates(
    memory: EvolutionMemory,
    failure_patterns: list[FailurePattern],
    advisor: Optional[CLIAdvisor] = None,
    max_mutations: int = 3,
) -> list[PromptVersion]:
    """GEPA-style evolutionary prompt improvement.

    Strategy:
    1. Get current best templates (by Thompson Sampling / CMP)
    2. Mutate: inject failure-avoidance clauses
    3. Crossover: combine elements from top templates
    4. Save new versions

    Bounded: max 3 mutations per cycle (Aider pattern).
    """
    new_versions = []
    stats = memory.get_template_stats()

    if not stats:
        logger.info("[LEARN] No templates to evolve yet")
        return new_versions

    # Sort by CMP score — focus evolution on top performers
    top_templates = [s for s in stats if s["successes"] + s["failures"] >= 2]
    if not top_templates:
        top_templates = stats[:3]

    mutations_done = 0

    for template_stat in top_templates[:max_mutations]:
        tid = template_stat["template_id"]
        current_prompt = memory.get_current_prompt(tid)
        if not current_prompt:
            continue

        # Mutate: inject failure-avoidance clauses from observed patterns
        relevant_patterns = [
            p for p in failure_patterns
            if p.frequency >= 2
        ]

        if not relevant_patterns:
            continue

        mutated = _apply_mutations(current_prompt, relevant_patterns)
        if mutated == current_prompt:
            continue

        pv = memory.save_prompt_version(
            template_id=tid,
            content=mutated,
            metadata={
                "evolution": "mutation",
                "patterns_applied": [p.pattern_type for p in relevant_patterns[:3]],
                "parent_cmp": template_stat["cmp"],
            },
        )
        new_versions.append(pv)
        mutations_done += 1
        logger.info(f"[LEARN] Mutated template {tid} → v{pv.version}")

        if mutations_done >= max_mutations:
            break

    return new_versions


def _apply_mutations(
    template: str,
    patterns: list[FailurePattern],
) -> str:
    """Inject failure-avoidance clauses into a template."""
    additions = []

    for pattern in patterns[:3]:
        if pattern.pattern_type == "timeout":
            additions.append("- Keep changes minimal to avoid timeout")
        elif pattern.pattern_type == "lint":
            additions.append("- Run linter before committing (black --check / eslint)")
        elif pattern.pattern_type == "test":
            additions.append("- Ensure all existing tests still pass before adding new ones")
        elif pattern.pattern_type == "stuck":
            additions.append("- If stuck after 2 attempts, simplify the approach")
        elif pattern.pattern_type == "compile":
            additions.append("- Verify all imports exist before using them")
        elif pattern.pattern_type == "missing_file":
            additions.append("- Check file existence before modifying")

    if not additions:
        return template

    # Insert before "## Do NOT" section if it exists, or append
    injection = "\n## Learned Constraints (auto-evolved)\n" + "\n".join(additions) + "\n"

    if "## Do NOT" in template:
        return template.replace("## Do NOT", injection + "\n## Do NOT")
    return template + "\n" + injection


def prune_templates(
    memory: EvolutionMemory,
    min_uses: int = 5,
    min_cmp: float = 0.2,
) -> list[str]:
    """Remove underperforming templates (GEPA Pareto pruning).

    Only prune templates with enough data (min_uses) and
    clearly poor performance (below min_cmp).
    """
    stats = memory.get_template_stats()
    pruned = []

    for s in stats:
        total = s["successes"] + s["failures"]
        if total >= min_uses and s["cmp"] < min_cmp:
            pruned.append(s["template_id"])
            logger.info(
                f"[LEARN] Pruning template {s['template_id']} "
                f"(CMP={s['cmp']:.3f}, uses={total})"
            )

    return pruned


async def learn_phase(
    build_results: list[BuildResult],
    review_verdicts: list[ReviewVerdict],
    project: str,
    memory: Optional[EvolutionMemory] = None,
    advisors: Optional[list[CLIAdvisor]] = None,
    evolve_this_cycle: bool = True,
) -> EvolutionResult:
    """Run the full Learn Phase.

    1. Update Thompson Sampling from build+review outcomes
    2. Extract failure patterns from trajectory history
    3. Evolve templates (if enabled this cycle)
    4. Prune underperformers
    """
    result = EvolutionResult()

    if not memory:
        logger.warning("[LEARN] No memory configured, skipping learn phase")
        return result

    # 1. Update Thompson Sampling stats from this cycle's results
    for br in build_results:
        if br.trajectory:
            success = br.status == "completed"
            # Also factor in review verdict
            matching_verdict = None
            for rv in review_verdicts:
                if rv.status == "approve":
                    matching_verdict = rv
                    break

            final_success = success and (matching_verdict is not None or not review_verdicts)
            memory.record_template_outcome(
                br.trajectory.template_id,
                success=final_success,
            )
            result.thompson_updates += 1

    logger.info(f"[LEARN] Updated {result.thompson_updates} Thompson Sampling stats")

    # 2. Extract failure patterns from history
    trajectories = memory.load_trajectories(project, limit=50)
    patterns = extract_failure_patterns(trajectories)
    result.failure_patterns_found = len(patterns)

    if patterns:
        logger.info(
            f"[LEARN] Found {len(patterns)} failure patterns: "
            + ", ".join(f"{p.pattern_type}({p.frequency}x)" for p in patterns[:5])
        )

    # 3. Evolve templates (GEPA mutation)
    if evolve_this_cycle and patterns:
        advisor = None
        if advisors:
            advisor = advisors[0]

        new_versions = await evolve_templates(
            memory, patterns, advisor=advisor, max_mutations=3,
        )
        result.templates_mutated = len(new_versions)
        result.prompt_versions_created = len(new_versions)

    # 4. Prune underperformers
    pruned = prune_templates(memory)
    result.templates_pruned = len(pruned)

    logger.info(
        f"[LEARN] {project}: "
        f"mutated={result.templates_mutated}, "
        f"pruned={result.templates_pruned}, "
        f"patterns={result.failure_patterns_found}, "
        f"thompson_updates={result.thompson_updates}"
    )

    return result
