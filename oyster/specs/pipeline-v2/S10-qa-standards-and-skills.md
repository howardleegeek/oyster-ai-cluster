---
task_id: S10-qa-standards-and-skills
project: pipeline-v2
priority: 1
depends_on: []
modifies: ["dispatch/pipeline/qa_standards.py", "dispatch/pipeline/skill_prompts.py"]
executor: glm
---

## 目标
新建两个基础模块: qa_standards.py (质量标准定义+检查函数) 和 skill_prompts.py (从 ~/.claude/skills/ 加载 skill 知识注入 prompt)

## 约束
- 只用标准库，不引入新 pip 依赖
- qa_standards.py 只做纯数据/数值检查，不调外部 API
- skill_prompts.py 必须从文件读取 SKILL.md，不硬编码内容
- 所有函数用 kwargs 不用位置参数
- 不动任何已有文件

## 具体改动

### dispatch/pipeline/qa_standards.py

```python
#!/usr/bin/env python3
"""Pipeline v2 质量标准定义"""
import json
from pathlib import Path

# === 质量阈值 ===
API_BYZANTINE_THRESHOLD = 0.9   # 拜占庭测试通过率 >= 90%
UI_SCORE_MIN = 70               # UI 评分 >= 70/100
COVERAGE_MIN = 50               # 测试覆盖率 >= 50%
PAGE_LOAD_MAX_SECONDS = 3.0     # 页面加载 < 3s
MAX_S1_BUGS = 0                 # 0 个 S1 bug
MAX_S2_BUGS = 3                 # <= 3 个 S2 bug
BROWSER_JS_ERRORS_MAX = 0       # 0 JS 错误
CONSECUTIVE_PASS_REQUIRED = 3   # 连续 3 次 L4 全通过才算 DONE

def check_api_qa(*, report: dict) -> tuple:
    """检查 API QA 报告 → (pass: bool, score: float, details: dict)"""
    total = report.get("total_tests", 0)
    passed = report.get("passed_tests", 0)
    score = (passed / total * 100) if total > 0 else 0
    byzantine_pass = report.get("byzantine_pass_rate", 0)
    ok = byzantine_pass >= API_BYZANTINE_THRESHOLD and report.get("s1_bugs", 0) == 0
    return (ok, score, {"byzantine_rate": byzantine_pass, "total": total, "passed": passed})

def check_browser_qa(*, report: dict) -> tuple:
    """检查浏览器 QA 报告 → (pass, score, details)"""
    js_errors = report.get("total_js_errors", 0)
    pages_ok = report.get("pages_loaded", 0)
    pages_total = report.get("pages_total", 0)
    e2e_pass = report.get("e2e_pass", False)
    score = (pages_ok / pages_total * 100) if pages_total > 0 else 0
    ok = js_errors <= BROWSER_JS_ERRORS_MAX and pages_ok == pages_total and e2e_pass
    return (ok, score, {"js_errors": js_errors, "pages_ok": pages_ok, "e2e_pass": e2e_pass})

def check_ui_qa(*, report: dict) -> tuple:
    """检查 UI 评审报告 → (pass, score, details)"""
    pages = report.get("pages", [])
    if not pages:
        return (True, 100, {"message": "no pages to check"})
    scores = [p.get("total_score", 0) for p in pages]
    avg = sum(scores) / len(scores)
    min_score = min(scores)
    overflow_count = sum(1 for p in pages if p.get("has_overflow", False))
    ok = min_score >= UI_SCORE_MIN and overflow_count == 0
    return (ok, avg, {"min_score": min_score, "avg_score": avg, "overflow_count": overflow_count})

def check_regression(*, report: dict) -> tuple:
    """检查回归测试报告 → (pass, score, details)"""
    coverage = report.get("coverage_percent", 0)
    new_failures = report.get("new_failures", [])
    load_times = report.get("page_load_times", {})
    slow_pages = {url: t for url, t in load_times.items() if t > PAGE_LOAD_MAX_SECONDS}
    ok = coverage >= COVERAGE_MIN and len(new_failures) == 0 and len(slow_pages) == 0
    score = coverage
    return (ok, score, {"coverage": coverage, "new_failures": new_failures, "slow_pages": slow_pages})

def check_all(*, project: str, reports_dir: str) -> dict:
    """汇总所有 L4 子报告 → overall verdict"""
    rd = Path(reports_dir)
    results = {}
    for sub, checker in [("L4a", check_api_qa), ("L4b", check_browser_qa), ("L4c", check_ui_qa), ("L4d", check_regression)]:
        report_file = rd / f"{sub}-report.json" if sub != "L4a" else rd / "L4a-api-report.json"
        # 尝试多种文件名
        for fname in [f"{sub}-report.json", f"{sub}-api-report.json", f"{sub}-browser-report.json", f"{sub}-ui-report.json", f"{sub}-regression-report.json"]:
            p = rd / fname
            if p.exists():
                report_file = p
                break
        if report_file.exists():
            report = json.loads(report_file.read_text())
            ok, score, details = checker(report=report)
            results[sub] = {"pass": ok, "score": score, "details": details}
        else:
            results[sub] = {"pass": False, "score": 0, "details": {"error": f"report not found: {report_file}"}}

    all_pass = all(r["pass"] for r in results.values())
    avg_score = sum(r["score"] for r in results.values()) / max(len(results), 1)
    return {"project": project, "overall_pass": all_pass, "avg_score": avg_score, "sub_results": results}
```

### dispatch/pipeline/skill_prompts.py

```python
#!/usr/bin/env python3
"""Skill Prompt 加载器 — 从 ~/.claude/skills/ 读取 SKILL.md 注入 agent prompt"""
from pathlib import Path

SKILL_DIR = Path.home() / ".claude" / "skills"

# 每层对应的 skill 列表
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
            skill_sections.append(f"### Skill: {s}\n{content}")

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
```

## 验收标准
- [ ] `python3 -c "from qa_standards import check_all; print('ok')"` 在 pipeline/ 目录下不报错
- [ ] `python3 -c "from skill_prompts import load_skill; print(len(load_skill(name='senior-qa')))"` 返回 > 0
- [ ] `python3 -c "from skill_prompts import build_layer_prompt; p=build_layer_prompt(layer='L4a', project_name='test', context={}); print(len(p))"` 返回 > 100
- [ ] check_all 对缺失报告返回 pass=False
- [ ] 所有函数使用 kwargs

## 不要做
- 不要安装新 pip 包
- 不要硬编码 SKILL.md 内容
- 不要修改任何已有文件
- 不要修改 LAYER_SKILLS 之外的任何配置
