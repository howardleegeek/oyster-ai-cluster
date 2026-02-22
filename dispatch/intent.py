#!/usr/bin/env python3
"""
Intent → Spec Pipeline
Howard: "修复登录bug"
  ↓
LLM 理解意图 + 读取 CLAUDE.md
  ↓
自动生成 S01-xxx.md spec
  ↓
dispatch 分配到最优节点
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import subprocess

DISPATCH_DIR = Path.home() / "Downloads" / "dispatch"
SPECS_DIR = Path.home() / "Downloads" / "specs"


def log(msg):
    print(f"[Intent] {msg}")


def read_claude_md(project):
    """Read project CLAUDE.md for context"""
    paths = [
        Path.home() / "Downloads" / project / "CLAUDE.md",
        SPECS_DIR / project / "CLAUDE.md",
    ]

    for p in paths:
        if p.exists():
            log(f"Reading CLAUDE.md from {p}")
            return p.read_text()[:5000]  # Limit context

    return ""


def call_llm(prompt, model="minimax"):
    """Call LLM to generate spec"""
    # Try using mm CLI if available
    mm_path = Path.home() / "bin" / "mm"

    if mm_path.exists():
        result = subprocess.run(
            [str(mm_path), prompt],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return result.stdout

    # Fallback: use openai or direct API
    log("Warning: Using fallback LLM call")
    return generate_spec_fallback(prompt)


def generate_spec_fallback(prompt):
    """Fallback spec generation without LLM"""
    # Extract key info from prompt
    lines = prompt.split("\n")
    intent = ""
    for line in lines:
        if "intent" in line.lower():
            intent = line.split(":", 1)[-1].strip()
            break

    if not intent:
        intent = prompt[:200]

    # Generate basic spec
    task_id = f"S{datetime.now().strftime('%m%d')}-auto"

    spec = f"""---
task_id: {task_id}
project: auto-generated
priority: 2
depends_on: []
modifies: []
executor: glm
---

## 目标
{intent}

## 具体改动
[需要 LLM 补充具体改动]

## 验收标准
- [ ] 功能正常工作

## 不要做
- 不修改无关代码
"""
    return spec


def generate_spec_from_intent(project, intent, context=""):
    """Generate spec from intent using LLM"""

    claude_md = read_claude_md(project)

    prompt = f"""Generate a dispatch spec from this intent.

## Project Context (CLAUDE.md)
{claude_md}

## Intent
{intent}

## Requirements
1. Fill in the YAML front-matter with:
   - task_id: Use format SYYMMDD-nnn (e.g., S260213-001)
   - project: {project}
   - priority: 1-3 (1=highest)
   - depends_on: list of task IDs this depends on
   - modifies: list of files/paths to modify

2. Write具体改动 section:
   - List specific files to create/modify
   - Include implementation details

3. Write 验收标准 section:
   - List testable acceptance criteria

4. Write 不要做 section:
   - List what NOT to do

Output ONLY the spec in Markdown format with YAML front-matter. No explanations.
"""

    spec = call_llm(prompt)

    # If LLM failed, use fallback
    if not spec or len(spec) < 100:
        log("Using fallback spec generation")
        spec = generate_spec_fallback(intent)

    return spec


def save_spec(project, spec):
    """Save spec to specs directory"""
    # Parse task_id from spec
    task_id = "S99-unknown"
    for line in spec.split("\n"):
        if line.startswith("task_id:"):
            task_id = line.split(":", 1)[-1].strip()
            break

    # Create project dir
    project_spec_dir = SPECS_DIR / project
    project_spec_dir.mkdir(parents=True, exist_ok=True)

    # Save spec
    spec_file = project_spec_dir / f"{task_id}.md"
    spec_file.write_text(spec)

    log(f"Saved spec to {spec_file}")
    return spec_file, task_id


def main():
    parser = argparse.ArgumentParser(description="Intent → Spec Pipeline")
    parser.add_argument("project", help="Project name")
    parser.add_argument("intent", help="Intent/direction from Howard")
    parser.add_argument("--no-dispatch", action="store_true", help="Don't run dispatch")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show spec without saving"
    )

    args = parser.parse_args()

    log(f"Project: {args.project}")
    log(f"Intent: {args.intent}")

    # Generate spec
    spec = generate_spec_from_intent(args.project, args.intent)

    if args.dry_run:
        print("\n=== Generated Spec ===")
        print(spec)
        return

    # Save spec
    spec_file, task_id = save_spec(args.project, spec)

    log(f"Generated spec: {task_id}")

    if not args.no_dispatch:
        log("Starting dispatch...")
        result = subprocess.run(
            ["python3", str(DISPATCH_DIR / "dispatch.py"), "start", args.project],
            capture_output=True,
            text=True,
            timeout=30,
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)


if __name__ == "__main__":
    main()
