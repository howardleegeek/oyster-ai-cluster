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
        (r"\bTODO\b", "TODO"),
        (r"\bFIXME\b", "FIXME"),
        (r"\bplaceholder\b", "placeholder"),
        (r"\bmock\b", "mock"),
        (r"\bhardcoded?\b", "hardcode"),
        (r"raise\s+NotImplementedError", "not_implemented"),
        (r"pass\s*#", "stub"),
        (r"return\s+\[\].*#.*placeholder", "empty_return"),
        (r"localhost:\d+", "localhost_url"),
    ]

    # 跳过的目录
    SKIP_DIRS = {
        "node_modules",
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "dist",
        "build",
        ".next",
    }
    # 扫描的文件后缀
    SCAN_EXTS = {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".html",
        ".css",
        ".yaml",
        ".yml",
        ".json",
        ".toml",
    }

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
                            gaps.append(
                                {
                                    "file": rel_path,
                                    "line": line_no,
                                    "tag": tag,
                                    "content": line.strip()[:200],
                                }
                            )

                # 检测 API endpoints (FastAPI/Express)
                # First, get router prefixes from this file
                router_prefixes = {}
                for m in re.finditer(
                    r'router\s*=\s*APIRouter\s*\(\s*prefix\s*=\s*["\']([^"\']+)["\']',
                    content,
                ):
                    # Extract prefix - will apply to routes in this file
                    pass

                # Extract all routes from @app and @router decorators
                for m in re.finditer(
                    r'@app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)', content
                ):
                    endpoints.append(
                        {
                            "method": m.group(1).upper(),
                            "path": m.group(2),
                            "file": rel_path,
                        }
                    )

                # For router routes, need to find the prefix from the same file
                # Find all APIRouter declarations with prefixes
                router_prefixes = {}
                for m in re.finditer(
                    r'router\s*=\s*APIRouter\s*\(\s*prefix\s*=\s*["\']([^"\']+)["\']',
                    content,
                ):
                    prefix = m.group(1)
                    # This prefix applies to routes in this file
                    # We'll apply it when we find routes

                for m in re.finditer(
                    r'router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)',
                    content,
                ):
                    # Find the router prefix for this file - look for APIRouter declaration before this route
                    # Simple heuristic: check if there's an APIRouter with prefix in the file
                    prefix = ""
                    # Try to find prefix in the same content
                    prefix_match = re.search(
                        r'router\s*=\s*APIRouter\s*\(\s*prefix\s*=\s*["\']([^"\']+)["\']',
                        content,
                    )
                    if prefix_match:
                        prefix = prefix_match.group(1)

                    full_path = prefix + m.group(2) if prefix else m.group(2)
                    endpoints.append(
                        {
                            "method": m.group(1).upper(),
                            "path": full_path,
                            "file": rel_path,
                        }
                    )

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
        (report_dir / "L1-gap-report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False)
        )

        result.finish("PASS", report=report)
        return result
