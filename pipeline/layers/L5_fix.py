#!/usr/bin/env python3
"""L5: 修复层 — 读 L4 bug report → 生成修复 spec → dispatch 执行"""

import json
from pathlib import Path
from layers.base import Layer, LayerResult


class L5Fix(Layer):
    name = "L5"
    max_retries = 2
    required_prev = ["L4"]

    def execute(self, project_config, prev_results: dict) -> LayerResult:
        result = LayerResult(layer=self.name, status="RUNNING")
        from executors import get_executor

        opencode = get_executor("opencode")

        # 测试 OpenCode 是否可用
        test_result = opencode.run("test", timeout=10)
        if not test_result.success:
            result.finish(
                "PASS", report={"message": "OpenCode 不可用，跳过 L5", "fixes": 0}
            )
            return result

        # 读 L4 bug report
        l4 = prev_results.get("L4")
        if not l4 or not l4.report:
            result.finish("FAIL", error="L4 report 缺失")
            return result

        bugs = l4.report.get("bugs", [])
        if not bugs:
            result.finish("PASS", report={"message": "无 bug，跳过", "fixes": 0})
            return result

        # 按 severity 排序 (S1 优先)
        bugs.sort(key=lambda b: b.get("severity", "S3"))

        # 生成修复 prompt
        bug_desc = []
        for i, bug in enumerate(bugs[:20]):  # 最多 20 个
            bug_desc.append(
                f"{i + 1}. [{bug['severity']}] {bug['type']}: {bug['description']}\n"
                f"   详情: {bug.get('detail', 'N/A')[:200]}"
            )

        prompt = f"""你是高级工程师。修复以下项目的 bug。

项目: {project_config.name} (tech: {project_config.stack})
项目路径: {project_config.path}

Bug 列表:
{chr(10).join(bug_desc)}

要求:
1. 每个 bug 给出具体的代码修复（文件路径 + 修改内容）
2. S1 bug 必须修（崩溃/数据丢失）
3. S2 bug 尽量修（功能异常）
4. 不要改 UI/CSS
5. 不要重构不相关代码
6. 用 kwargs 不用位置参数

输出: 每个修复标明文件路径、修改前、修改后。"""

        opencode = get_executor("opencode")
        fix_result = opencode.run(prompt, cwd=project_config.path, timeout=600)

        # 写修复 spec
        specs_dir = Path(__file__).parent.parent.parent / "specs" / project_config.name
        specs_dir.mkdir(parents=True, exist_ok=True)

        spec_file = specs_dir / f"FIX-{project_config.name}-bugs.md"
        spec_content = f"""---
task_id: FIX-{project_config.name}
project: {project_config.name}
priority: 1
depends_on: []
executor: glm

## 目标
修复 L4 发现的 {len(bugs)} 个 bug

## Bug 列表
{chr(10).join(bug_desc)}

## AI 生成的修复方案
{fix_result.stdout if fix_result.success else "生成失败: " + fix_result.stderr}

## 约束
- 不动 UI/CSS
- 只修 bug，不重构
- kwargs only
"""
        spec_file.write_text(spec_content)

        # dispatch 执行修复
        dispatch = get_executor("dispatch")
        dispatch_result = dispatch.start_and_wait(project_config.name)

        report = {
            "bugs_found": len(bugs),
            "s1_count": len([b for b in bugs if b["severity"] == "S1"]),
            "s2_count": len([b for b in bugs if b["severity"] == "S2"]),
            "fix_spec": str(spec_file),
            "dispatch_success": dispatch_result.success,
        }

        if dispatch_result.success:
            result.finish("PASS", report=report)
        else:
            result.finish("FAIL", report=report, error=dispatch_result.stderr[:500])

        return result
