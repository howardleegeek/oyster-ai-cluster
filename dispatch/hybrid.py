#!/usr/bin/env python3
"""
Hybrid Router - 智能选择 Antfarm 或 Dispatch

用法:
  python3 hybrid.py "修复登录bug"

系统会自动选择:
  - 简单/单任务 → Antfarm (bug-fix, feature-dev)
  - 复杂/多任务 → Dispatch (37 slots)
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

DISPATCH_DIR = Path.home() / "Downloads" / "dispatch"
SPECS_DIR = Path.home() / "Downloads" / "specs"


def log(msg):
    print(f"[Hybrid] {msg}")


def analyze_intent(intent: str) -> dict:
    """分析意图，决定用哪个系统"""

    intent_lower = intent.lower()

    # Antfarm 擅长的任务类型
    antfarm_keywords = [
        "bug",
        "fix",
        "修复",
        "错误",
        "feature",
        "功能",
        "添加",
        "security",
        "安全",
        "漏洞",
        "refactor",
        "重构",
    ]

    # Dispatch 擅长的任务类型
    dispatch_keywords = [
        "批量",
        "batch",
        "多个",
        "并行",
        "parallel",
        "分布式",
        "distributed",
        "测试",
        "test",
        "验收",
        "部署",
        "deploy",
    ]

    antfarm_score = sum(1 for k in antfarm_keywords if k in intent_lower)
    dispatch_score = sum(1 for k in dispatch_keywords if k in intent_lower)

    # 决定用哪个
    if antfarm_score > dispatch_score:
        return {
            "system": "antfarm",
            "workflow": "bug-fix"
            if any(x in intent_lower for x in ["bug", "fix", "修复", "错误"])
            else "feature-dev",
            "reason": f"Antfarm更适合 (score: {antfarm_score})",
        }
    elif dispatch_score > antfarm_score:
        return {
            "system": "dispatch",
            "workflow": None,
            "reason": f"Dispatch更适合 (score: {dispatch_score})",
        }
    else:
        # 默认用 Antfarm (更简单)
        return {
            "system": "antfarm",
            "workflow": "feature-dev",
            "reason": "默认用Antfarm (更简单)",
        }


def run_antfarm(workflow: str, intent: str) -> bool:
    """运行 Antfarm"""
    log(f"使用 Antfarm workflow: {workflow}")

    cmd = ["antfarm", "workflow", "run", workflow, intent]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except Exception as e:
        log(f"Antfarm error: {e}")
        return False


def run_dispatch(project: str, intent: str) -> bool:
    """运行 Dispatch"""
    log(f"使用 Dispatch (project: {project})")

    # 生成 spec
    spec_content = f"""---
task_id: S{datetime.now().strftime("%m%d")}-hybrid
project: {project}
priority: 2
depends_on: []
---

## 目标
{intent}

## 具体改动
[由dispatch + LLM生成具体spec]
"""

    # 保存 spec
    spec_file = SPECS_DIR / project / f"S{datetime.now().strftime('%m%d')}-hybrid.md"
    spec_file.parent.mkdir(parents=True, exist_ok=True)
    spec_file.write_text(spec_content)

    log(f"Saved spec: {spec_file}")

    # 运行 dispatch
    cmd = ["python3", str(DISPATCH_DIR / "dispatch.py"), "start", project]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        print(result.stdout)
        return result.returncode == 0
    except Exception as e:
        log(f"Dispatch error: {e}")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Hybrid Router - 智能选择系统")
    parser.add_argument("intent", nargs="?", help="任务描述")
    parser.add_argument("--project", default="clawmarketing", help="项目名")
    parser.add_argument(
        "--force", choices=["antfarm", "dispatch"], help="强制使用某系统"
    )
    parser.add_argument("--list", action="store_true", help="列出可用工作流")

    args = parser.parse_args()

    if args.list or not args.intent:
        # 列出所有可用选项
        print("=== Antfarm Workflows ===")
        # 列出所有可用选项
        print("=== Antfarm Workflows ===")
        try:
            subprocess.run(["antfarm", "workflow", "list"])
        except:
            print("(未安装)")

        print("\n=== Dispatch Projects ===")
        for p in SPECS_DIR.iterdir():
            if p.is_dir() and not p.name.startswith("."):
                print(f"  - {p.name}")
        return

    intent = args.intent

    # 分析意图
    decision = analyze_intent(intent)

    # 强制选择
    if args.force:
        decision["system"] = args.force
        decision["reason"] = f"强制使用: {args.force}"

    log(f"意图: {intent}")
    log(f"决策: {decision['reason']}")

    # 执行
    if decision["system"] == "antfarm":
        run_antfarm(decision["workflow"], intent)
    else:
        run_dispatch(args.project, intent)


if __name__ == "__main__":
    main()
