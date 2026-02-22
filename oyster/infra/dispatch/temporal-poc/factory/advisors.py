"""
Advisor Wrappers — Three advisors using three different CLI tools.

Each advisor uses a different CLI for maximum diversity:
- Advisor 1 (opus): Claude CLI (`claude -p`) — strongest reasoning
- Advisor 2 (codex): Antigravity Codex CLI (`codex exec`) — code-focused
- Advisor 3 (antigravity): opencode CLI (`opencode run`) — free GLM model

Each advisor runs independently (no shared context) to avoid anchoring bias.
Results are synthesized by the Think phase for consensus.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger("factory.advisors")


@dataclass
class AdvisorOpinion:
    """Structured output from an advisor."""

    advisor_name: str
    analysis: str  # free-form analysis text
    recommendations: list[str]  # actionable items
    risks: list[str]  # identified risks or blind spots
    confidence: float  # 0.0 - 1.0
    raw_response: str = ""
    error: str = ""

    @property
    def is_valid(self) -> bool:
        return bool(self.analysis) and not self.error


def _clean_output(raw: str) -> str:
    """Strip ANSI codes, control chars, and CLI UI noise."""
    # Strip ANSI escape sequences
    raw = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', raw)
    # Strip other control characters (keep newlines and tabs)
    raw = re.sub(r'[\x00-\x08\x0e-\x1f\x7f]', '', raw)
    # Remove UI noise lines (prompts, build lines, spinners)
    lines = []
    for line in raw.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('>'):
            continue
        if stripped.startswith('build '):
            continue
        lines.append(line)
    return '\n'.join(lines).strip()


def _parse_advisor_response(advisor_name: str, raw: str) -> AdvisorOpinion:
    """Parse structured or plain text response into AdvisorOpinion."""
    try:
        if "```json" in raw:
            json_start = raw.index("```json") + 7
            json_end = raw.index("```", json_start)
            parsed = json.loads(raw[json_start:json_end])
        elif raw.strip().startswith("{"):
            parsed = json.loads(raw.strip())
        else:
            # Try to find JSON object in the text
            match = re.search(r'\{[^{}]*"analysis"[^{}]*\}', raw, re.DOTALL)
            if match:
                parsed = json.loads(match.group())
            else:
                parsed = None

        if parsed:
            # Ensure recommendations are strings
            recs = parsed.get("recommendations", [])
            recs = [str(r) if not isinstance(r, str) else r for r in recs]
            risks = parsed.get("risks", [])
            risks = [str(r) if not isinstance(r, str) else r for r in risks]

            return AdvisorOpinion(
                advisor_name=advisor_name,
                analysis=str(parsed.get("analysis", raw)),
                recommendations=recs,
                risks=risks,
                confidence=float(parsed.get("confidence", 0.7)),
                raw_response=raw,
            )
    except (json.JSONDecodeError, ValueError):
        pass

    # Plain text fallback — still valid, just no structured recs
    return AdvisorOpinion(
        advisor_name=advisor_name,
        analysis=raw[:2000], recommendations=[], risks=[],
        confidence=0.6, raw_response=raw,
    )


# ── CLI Runner Functions ──


async def _run_claude(prompt: str, timeout: int = 120) -> str:
    """Run Claude CLI in print mode. Returns cleaned output."""
    claude_bin = shutil.which("claude")
    if not claude_bin:
        raise FileNotFoundError("claude CLI not found in PATH")

    proc = await asyncio.create_subprocess_exec(
        claude_bin, "-p",
        "--model", "sonnet",
        "--no-session-persistence",
        "--allowedTools", "",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env={**os.environ, "PAGER": "cat", "GIT_PAGER": "cat"},
    )
    stdout, _ = await asyncio.wait_for(
        proc.communicate(input=prompt.encode("utf-8")),
        timeout=timeout,
    )
    raw = stdout.decode("utf-8", errors="replace")
    return _clean_output(raw)


async def _run_codex(prompt: str, timeout: int = 120) -> str:
    """Run Codex CLI in exec mode. Returns cleaned output."""
    codex_bin = shutil.which("codex")
    if not codex_bin:
        raise FileNotFoundError("codex CLI not found in PATH")

    proc = await asyncio.create_subprocess_exec(
        codex_bin, "exec",
        "--sandbox", "read-only",
        prompt,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env={**os.environ, "PAGER": "cat", "GIT_PAGER": "cat", "CI": "1"},
    )
    stdout, _ = await asyncio.wait_for(
        proc.communicate(),
        timeout=timeout,
    )
    raw = stdout.decode("utf-8", errors="replace")
    return _clean_output(raw)


async def _run_opencode(
    model: str,
    prompt: str,
    timeout: int = 60,
) -> str:
    """Run opencode CLI with a specific model. Returns cleaned output."""
    opencode_bin = shutil.which("opencode")
    if not opencode_bin:
        alt = str(Path.home() / ".opencode" / "bin" / "opencode")
        if Path(alt).exists():
            opencode_bin = alt
        else:
            raise FileNotFoundError("opencode not found in PATH or ~/.opencode/bin/")

    proc = await asyncio.create_subprocess_exec(
        opencode_bin, "run", "-m", model,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env={**os.environ, "PAGER": "cat", "GIT_PAGER": "cat", "CI": "1"},
    )
    stdout, _ = await asyncio.wait_for(
        proc.communicate(input=prompt.encode("utf-8")),
        timeout=timeout,
    )
    raw = stdout.decode("utf-8", errors="replace")
    return _clean_output(raw)


# ── CLIAdvisor ──


class CLIAdvisor:
    """Advisor that uses a CLI tool (claude, codex, or opencode)."""

    def __init__(
        self,
        name: str,
        cli_type: str,       # "claude" | "codex" | "opencode"
        role_prompt: str,
        model: str = "",     # only used for opencode
        timeout: int = 120,
    ):
        self.name = name
        self.cli_type = cli_type
        self.model = model
        self.role_prompt = role_prompt
        self.timeout = timeout

    async def think(
        self,
        context: str,
        question: str,
        codebase_summary: str = "",
    ) -> AdvisorOpinion:
        """Get this advisor's independent opinion."""
        prompt = (
            f"{self.role_prompt}\n\n"
            f"## Codebase\n{codebase_summary[:2000] if codebase_summary else 'N/A'}\n\n"
            f"## Context\n{context[:1500]}\n\n"
            f"## Question\n{question}\n\n"
            "Respond in JSON:\n"
            '{"analysis": "your analysis", '
            '"recommendations": ["action 1", "action 2"], '
            '"risks": ["risk 1"], '
            '"confidence": 0.8}'
        )
        return await self._call(prompt)

    async def review(
        self,
        diff: str,
        spec: str,
        context: str = "",
    ) -> AdvisorOpinion:
        """Review a code change."""
        prompt = (
            f"{self.role_prompt}\n\n"
            "Review this code change.\n\n"
            f"## Spec\n{spec[:1500]}\n\n"
            f"## Diff\n{diff[:2000]}\n\n"
            "Respond in JSON:\n"
            '{"analysis": "your review", '
            '"recommendations": ["suggestion 1"], '
            '"risks": ["issue 1"], '
            '"confidence": 0.8}'
        )
        return await self._call(prompt)

    async def _call(self, prompt: str) -> AdvisorOpinion:
        try:
            if self.cli_type == "claude":
                raw = await _run_claude(prompt, self.timeout)
            elif self.cli_type == "codex":
                raw = await _run_codex(prompt, self.timeout)
            elif self.cli_type == "opencode":
                raw = await _run_opencode(self.model, prompt, self.timeout)
            else:
                raise ValueError(f"Unknown CLI type: {self.cli_type}")

            if not raw:
                return AdvisorOpinion(
                    advisor_name=self.name, analysis="", recommendations=[],
                    risks=[], confidence=0.0,
                    error=f"{self.cli_type} returned empty response",
                )
            return _parse_advisor_response(self.name, raw)
        except FileNotFoundError as e:
            return AdvisorOpinion(
                advisor_name=self.name, analysis="", recommendations=[],
                risks=[], confidence=0.0,
                error=f"{self.cli_type} CLI not found: {e}",
            )
        except asyncio.TimeoutError:
            return AdvisorOpinion(
                advisor_name=self.name, analysis="", recommendations=[],
                risks=[], confidence=0.0,
                error=f"{self.cli_type} timed out after {self.timeout}s",
            )
        except Exception as e:
            logger.error(f"Advisor {self.name} ({self.cli_type}) error: {e}")
            return AdvisorOpinion(
                advisor_name=self.name, analysis="", recommendations=[],
                risks=[], confidence=0.0, error=str(e),
            )


def create_advisors() -> list[CLIAdvisor]:
    """Create 3 advisors with different CLI backends for diversity.

    - opus: Claude CLI (Sonnet) — best at architecture & strategic thinking
    - codex: Antigravity Codex CLI — code-focused, practical engineering
    - antigravity: opencode CLI (GLM-5-free) — free model, contrarian perspective
    """
    return [
        CLIAdvisor(
            name="opus",
            cli_type="claude",
            role_prompt=(
                "You are a strategic technology advisor. "
                "Focus on architecture, product direction, and long-term impact. "
                "Think about what will matter in 6 months."
            ),
            timeout=120,
        ),
        CLIAdvisor(
            name="codex",
            cli_type="codex",
            role_prompt=(
                "You are a pragmatic senior engineer. "
                "Focus on code quality, feasibility, and tech debt. "
                "What's the simplest thing that could work?"
            ),
            timeout=120,
        ),
        CLIAdvisor(
            name="antigravity",
            cli_type="opencode",
            model="opencode/glm-5-free",
            role_prompt=(
                "You are a contrarian advisor. Challenge assumptions. "
                "Find blind spots others miss. "
                "What could go wrong? What's everyone overlooking?"
            ),
            timeout=60,
        ),
    ]


async def gather_opinions(
    advisors: list[CLIAdvisor],
    context: str,
    question: str,
    codebase_summary: str = "",
) -> list[AdvisorOpinion]:
    """Run all advisors in parallel and gather their independent opinions."""
    tasks = [
        advisor.think(context, question, codebase_summary)
        for advisor in advisors
    ]
    return list(await asyncio.gather(*tasks, return_exceptions=False))


async def gather_reviews(
    advisors: list[CLIAdvisor],
    diff: str,
    spec: str,
    context: str = "",
) -> list[AdvisorOpinion]:
    """Run all advisors' review in parallel."""
    tasks = [advisor.review(diff, spec, context) for advisor in advisors]
    return list(await asyncio.gather(*tasks, return_exceptions=False))
