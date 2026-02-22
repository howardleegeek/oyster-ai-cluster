"""
Review Phase — Multi-advisor code review + self-debug.

Sources:
- OpenHands: StuckDetector for detecting review loops
- Aider: Bounded reflection for self-debug
- AutoGen MagenticOne: Progress ledger self-assessment
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from .advisors import CLIAdvisor, create_advisors, gather_reviews
from .build import BuildResult

logger = logging.getLogger("factory.review")


@dataclass
class ReviewVerdict:
    """Final verdict from multi-advisor review."""

    status: str  # "approve" | "minor_issues" | "major_issues" | "reject"
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    advisor_summaries: dict[str, str] = field(default_factory=dict)

    @property
    def should_merge(self) -> bool:
        return self.status == "approve"

    @property
    def should_auto_fix(self) -> bool:
        return self.status == "minor_issues"

    @property
    def needs_rethink(self) -> bool:
        return self.status in ("major_issues", "reject")


async def review_phase(
    build_result: BuildResult,
    spec_content: str,
    advisors: Optional[list[CLIAdvisor]] = None,
) -> ReviewVerdict:
    """
    Run multi-advisor review on a build result.

    1. Gather reviews from all advisors in parallel
    2. Synthesize into a verdict
    3. Return approve / minor_issues / major_issues / reject
    """
    if build_result.status != "completed":
        return ReviewVerdict(
            status="reject",
            issues=[f"Build failed: {build_result.error[:200]}"],
        )

    if advisors is None:
        advisors = create_advisors()

    diff = build_result.diff or build_result.test_output or "(no diff available)"

    logger.info(f"[REVIEW] Reviewing {build_result.task_id} with {len(advisors)} advisors")

    opinions = await gather_reviews(
        advisors, diff=diff, spec=spec_content,
        context=f"Task: {build_result.task_id}, Duration: {build_result.duration_seconds:.0f}s"
    )

    # Synthesize verdict
    all_issues = []
    all_suggestions = []
    summaries = {}
    total_confidence = 0.0
    valid_count = 0

    for op in opinions:
        summaries[op.advisor_name] = op.analysis[:200] if op.is_valid else op.error
        if op.is_valid:
            all_issues.extend(op.risks)
            all_suggestions.extend(op.recommendations)
            total_confidence += op.confidence
            valid_count += 1

    if valid_count == 0:
        logger.warning("[REVIEW] No valid advisor responses — REJECTING (not auto-approving blind)")
        return ReviewVerdict(
            status="reject",
            issues=["No advisors responded — rejected for safety (was auto-approve, now fixed)"],
            advisor_summaries=summaries,
        )

    avg_confidence = total_confidence / valid_count

    # Classify issues by severity
    critical_keywords = [
        "security", "injection", "crash", "data loss", "breaking change",
        "regression", "memory leak", "deadlock",
    ]
    minor_keywords = [
        "style", "naming", "comment", "formatting", "typo",
        "documentation", "readability",
    ]

    critical_issues = [
        issue for issue in all_issues
        if any(kw in issue.lower() for kw in critical_keywords)
    ]
    minor_issues = [
        issue for issue in all_issues
        if any(kw in issue.lower() for kw in minor_keywords)
    ]
    medium_issues = [
        issue for issue in all_issues
        if issue not in critical_issues and issue not in minor_issues
    ]

    # Determine verdict
    if critical_issues:
        status = "reject"
    elif medium_issues and len(medium_issues) >= 2:
        status = "major_issues"
    elif minor_issues or (medium_issues and len(medium_issues) == 1):
        status = "minor_issues"
    elif avg_confidence < 0.4:
        status = "major_issues"
    else:
        status = "approve"

    verdict = ReviewVerdict(
        status=status,
        issues=critical_issues + medium_issues + minor_issues,
        suggestions=all_suggestions[:5],
        advisor_summaries=summaries,
    )

    logger.info(
        f"[REVIEW] {build_result.task_id}: {verdict.status} "
        f"({len(verdict.issues)} issues, confidence={avg_confidence:.2f})"
    )
    return verdict
