---
task_id: S04-L1-L2-layers
project: pipeline
priority: 2
depends_on: [S02, S03]
modifies: ["dispatch/pipeline/layers/L1_analyze.py", "dispatch/pipeline/layers/L2_implement.py"]
executor: glm
---

## 目标
实现 L1 分析层（扫描项目产出 gap-report）和 L2 实现层（gap → specs → dispatch）

## 要创建的文件

### 1. dispatch/pipeline/layers/L1_analyze.py

L1 的工作：扫描项目目录，找出所有 TODO/placeholder/mock，生成结构化 gap report。

```python
#!/usr/bin/env python3
"""L1: 项目分析层 — 扫描代码找出 gap"""
import os
import re
import json
from pathlib import Path
from layers.base import Layer, LayerResult

class L1Analyze(Layer):
    name = "L1"
    max_retries = 1  # 分析不需要重试
    required_prev = []

    # 扫描的模式
    PATTERNS = [
        (r'\bTODO\b', "TODO"),
        (r'\bFIXME\b', "FIXME"),
        (r'\bplaceholder\b', "placeholder"),
        (r'\bmock\b', "mock"),
        (r'\bhardcoded?\b', "hardcode"),
        (r'raise\s+NotImplementedError', "not_implemented"),
        (r'pass\s*#', "stub"),
        (r'return\s+\[\].*#.*placeholder', "empty_return"),
        (r'localhost:\d+', "localhost_url"),
    ]

    # 跳过的目录
    SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build", ".next"}
    # 扫描的文件后缀
    SCAN_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".yaml", ".yml", ".json", ".toml"}

    def execute(self, project_config, prev_results: dict) -> LayerResult:
        result = LayerResult(layer=self.name, status="RUNNING")
        project_path = Path(project_config.path).expanduser()

        if not project_path.exists():
            result.finish("FAIL", error=f"项目路径不存在: {project_path}")
            return result

        gaps = []
        file_count = 0
        real_features = []
        endpoints = []

        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]
            for fname in files:
                fpath = Path(root) / fname
                if fpath.suffix not in self.SCAN_EXTS:
                    continue
                file_count += 1
                try:
                    content = fpath.read_text(errors="ignore")
                except Exception:
                    continue

                rel_path = str(fpath.relative_to(project_path))

                # 扫描 gap
                for line_no, line in enumerate(content.splitlines(), 1):
                    for pattern, tag in self.PATTERNS:
                        if re.search(pattern, line, re.IGNORECASE):
                            gaps.append({
                                "file": rel_path,
                                "line": line_no,
                                "tag": tag,
                                "content": line.strip()[:200],
                            })

                # 检测 API endpoints (FastAPI/Express)
                for m in re.finditer(r'@app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)', content):
                    endpoints.append({"method": m.group(1).upper(), "path": m.group(2), "file": rel_path})
                for m in re.finditer(r'router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)', content):
                    endpoints.append({"method": m.group(1).upper(), "path": m.group(2), "file": rel_path})

        # 分类汇总
        gap_summary = {}
        for g in gaps:
            tag = g["tag"]
            gap_summary.setdefault(tag, []).append(g)

        report = {
            "project": project_config.name,
            "path": str(project_path),
            "files_scanned": file_count,
            "total_gaps": len(gaps),
            "gap_by_type": {k: len(v) for k, v in gap_summary.items()},
            "gaps": gaps[:500],  # 限制大小
            "endpoints": endpoints,
            "stack": project_config.stack,
        }

        # 保存详细报告
        report_dir = Path(__file__).parent.parent / "reports" / project_config.name
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "L1-gap-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))

        result.finish("PASS", report=report)
        return result
```

### 2. dispatch/pipeline/layers/L2_implement.py

L2 的工作：读 L1 gap report → 调 OpenCode 生成修复 specs → 写到 specs/ → 调 dispatch 分发执行。

```python
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
            result.finish("PASS", report={"message": "无 gap，跳过", "specs_generated": 0})
            return result

        # 按文件分组 gap
        file_gaps = {}
        for g in gaps:
            file_gaps.setdefault(g["file"], []).append(g)

        # 调 OpenCode 生成修复 spec
        from executors import get_executor
        opencode = get_executor("opencode")

        specs_dir = Path(__file__).parent.parent.parent / "specs" / project_config.name
        specs_dir.mkdir(parents=True, exist_ok=True)

        generated_specs = []
        # 按文件批量生成 spec（每 5 个文件一批）
        file_list = list(file_gaps.items())
        batch_size = 5

        for batch_idx in range(0, len(file_list), batch_size):
            batch = file_list[batch_idx:batch_idx + batch_size]
            batch_desc = []
            for fpath, fgaps in batch:
                gap_lines = [f"  - L{g['line']}: [{g['tag']}] {g['content'][:100]}" for g in fgaps[:10]]
                batch_desc.append(f"文件: {fpath}\n" + "\n".join(gap_lines))

            prompt = f"""你是高级工程师。为以下代码 gap 生成修复方案。

项目: {project_config.name} (tech: {project_config.stack})
项目路径: {project_config.path}

以下文件需要修复:
{'---'.join(batch_desc)}

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
{exec_result.stdout if exec_result.success else '生成失败: ' + exec_result.stderr}

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
```

## 验收标准
- [ ] `python3 pipeline.py run clawvision --layer L1` 生成 `reports/clawvision/L1-gap-report.json`
- [ ] L1 gap report 包含 files_scanned, total_gaps, gaps, endpoints
- [ ] L2 能读取 L1 report 并生成 spec 文件
- [ ] L2 调用 dispatch executor (可以先 mock dispatch 结果测试)

## 不要做
- 不要修改 dispatch.py
- 不要修改 base.py 或 pipeline.py
- 不要实现 L3-L6
