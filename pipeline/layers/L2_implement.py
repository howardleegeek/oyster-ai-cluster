#!/usr/bin/env python3
"""L2: 实现层 — gap → specs → dispatch"""

import json
from pathlib import Path
from layers.base import Layer, LayerResult


class L2Implement(Layer):
    name = "L2"
    max_retries = 2
    required_prev = ["L1"]

    def execute(self, project_config, prev_results: dict) -> LayerResult:
        result = LayerResult(layer=self.name, status="RUNNING")

        # 读 L1 gap report
        l1 = prev_results.get("L1")
        if not l1 or not l1.report:
            result.finish("FAIL", error="L1 report 缺失")
            return result

        gaps = l1.report.get("gaps", [])
        if not gaps:
            result.finish(
                "PASS", report={"message": "无 gap，跳过", "specs_generated": 0}
            )
            return result

        # 按文件分组 gap
        file_gaps = {}
        for g in gaps:
            file_gaps.setdefault(g["file"], []).append(g)

        # 调 OpenCode 生成修复 spec
        from executors import get_executor

        opencode = get_executor("opencode")

        # 测试 OpenCode 是否可用
        test_result = opencode.run("test", timeout=10)
        if not test_result.success:
            # OpenCode 不可用，跳过 L2
            result.finish(
                "PASS",
                report={"message": "OpenCode 不可用，跳过 L2", "specs_generated": 0},
            )
            return result

        specs_dir = Path(__file__).parent.parent.parent / "specs" / project_config.name
        specs_dir.mkdir(parents=True, exist_ok=True)

        generated_specs = []
        # 按文件批量生成 spec（每 5 个文件一批）
        file_list = list(file_gaps.items())
        batch_size = 5

        for batch_idx in range(0, len(file_list), batch_size):
            batch = file_list[batch_idx : batch_idx + batch_size]
            batch_desc = []
            for fpath, fgaps in batch:
                gap_lines = [
                    f"  - L{g['line']}: [{g['tag']}] {g['content'][:100]}"
                    for g in fgaps[:10]
                ]
                batch_desc.append(f"文件: {fpath}\n" + "\n".join(gap_lines))

            prompt = f"""你是高级工程师。为以下代码 gap 生成修复方案。

项目: {project_config.name} (tech: {project_config.stack})
项目路径: {project_config.path}

以下文件需要修复:
{"---".join(batch_desc)}

要求:
1. 每个文件输出具体的代码修改（不是伪代码）
2. placeholder 替换为真实实现
3. localhost URL 替换为环境变量
4. mock 数据替换为真实逻辑
5. 不要改 UI/CSS
6. 用 kwargs 不用位置参数

输出格式: 每个文件一段，标明文件路径和修改内容。"""

            exec_result = opencode.run(prompt, cwd=project_config.path)

            spec_id = f"S{batch_idx // batch_size + 1:02d}"
            spec_file = specs_dir / f"{spec_id}-batch-fix.md"
            spec_content = f"""---
task_id: {spec_id}-{project_config.name}
project: {project_config.name}
priority: 2
depends_on: []
modifies: {json.dumps([f for f, _ in batch])}
executor: glm
---

## 目标
修复以下文件中的 placeholder/TODO/mock

## AI 生成的修复方案
{exec_result.stdout if exec_result.success else "生成失败: " + exec_result.stderr}

## 原始 Gap
{json.dumps([{"file": f, "gaps": gs} for f, gs in batch], indent=2, ensure_ascii=False)}

## 约束
- 不动 UI/CSS
- 用环境变量替代 hardcoded URL
- kwargs only
"""
            spec_file.write_text(spec_content)
            generated_specs.append(str(spec_file))

        # 调 dispatch 分发执行
        dispatch = get_executor("dispatch")
        dispatch_result = dispatch.start_and_wait(project_config.name)

        report = {
            "specs_generated": len(generated_specs),
            "spec_files": generated_specs,
            "dispatch_success": dispatch_result.success,
            "dispatch_output": dispatch_result.stdout[:2000],
        }

        if dispatch_result.success:
            result.finish("PASS", report=report)
        else:
            result.finish("FAIL", report=report, error=dispatch_result.stderr[:500])

        return result
