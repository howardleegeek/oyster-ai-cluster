#!/usr/bin/env python3
"""Skill Prompt 加载器 — 从 ~/.claude/skills/ 读取 SKILL.md 注入 agent prompt"""
from pathlib import Path

SKILL_DIR = Path.home() / ".claude" / "skills"

LAYER_SKILLS = {
    "L1":  ["api-design-principles"],
    "L2":  ["code-reviewer", "frontend-design"],
    "L3":  ["database-migration"],
    "L4a": ["senior-qa", "api-testing-patterns", "security-compliance"],
    "L4b": ["senior-qa", "frontend-testing", "accessibility-testing"],
    "L4c": ["senior-qa", "frontend-design"],
    "L4d": ["senior-qa", "mutation-testing", "performance-testing"],
    "L5":  ["code-reviewer", "frontend-design", "senior-security"],
    "L6":  ["deployment-pipeline-design", "secrets-management", "error-tracking", "github-actions-templates", "creating-apm-dashboards"],
}

def load_skill(*, name: str) -> str:
    """读取单个 skill 的 SKILL.md 内容"""
    path = SKILL_DIR / name / "SKILL.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""

def build_layer_prompt(*, layer: str, project_name: str, context: dict) -> str:
    """为指定 layer 构建包含 skill 知识的完整 prompt"""
    skills = LAYER_SKILLS.get(layer, [])
    skill_sections = []
    for s in skills:
        content = load_skill(name=s)
        if content:
            skill_sections.append(f"### Skill: {s}\n{content}\n")

    skill_context = "\n---\n".join(skill_sections) if skill_sections else "(no skills loaded)"
    task_desc = context.get("task_description", "")
    project_info = context.get("project_info", "")

    return f"""你是 {layer} 工位的专家 agent。

## 你的技能知识
{skill_context}

## 任务
{task_desc}

## 项目: {project_name}
{project_info}
"""
