#!/usr/bin/env python3
"""L3: 构建层 — 依赖安装 + 编译 + 启动测试"""

import time
import json
from pathlib import Path
from layers.base import Layer, LayerResult


class L3Build(Layer):
    name = "L3"
    max_retries = 3
    required_prev = ["L2"]

    def execute(self, project_config, prev_results: dict) -> LayerResult:
        result = LayerResult(layer=self.name, status="RUNNING")
        from executors import get_executor

        local = get_executor("local")

        project_path = str(Path(project_config.path).expanduser())
        checks = {}

        # === 后端构建 ===
        if project_config.backend:
            be_path = str(Path(project_path) / project_config.backend.path)

            # 依赖安装
            req_file = Path(be_path) / "requirements.txt"
            if req_file.exists():
                r = local.run(
                    f"pip install -r requirements.txt 2>&1 | tail -5",
                    cwd=be_path,
                    timeout=120,
                )
                checks["backend_deps"] = {
                    "status": "PASS" if r.success else "FAIL",
                    "output": r.stdout[-500:],
                }

            # Python 编译检查
            r = local.run(
                "find . -name '*.py' -not -path './venv/*' -not -path './.venv/*' | head -50 | xargs -I{} python3 -m py_compile {}",
                cwd=be_path,
                timeout=60,
            )
            checks["backend_compile"] = {
                "status": "PASS" if r.success else "FAIL",
                "output": (r.stdout + r.stderr)[-500:],
            }

            # 启动测试 — 后台启动，等几秒，curl health
            cmd = project_config.backend.cmd
            port = project_config.backend.port
            health = project_config.backend.health

            # 先杀掉可能残留的进程
            local.run(
                f"lsof -ti:{port} | xargs kill -9 2>/dev/null || true", cwd=project_path
            )
            time.sleep(1)

            # 后台启动 - 从项目根目录运行
            local.run(
                f"nohup {cmd} --port {port} > /tmp/pipeline-backend-{project_config.name}.log 2>&1 &",
                cwd=project_path,
                timeout=5,
            )
            time.sleep(5)

            # 健康检查
            r = local.run(
                f"curl -sf http://localhost:{port}{health} -o /dev/null -w '%{{http_code}}'",
                timeout=10,
            )
            checks["backend_health"] = {
                "status": "PASS" if r.success else "FAIL",
                "output": r.stdout + r.stderr,
            }

            # 健康检查通过后，不杀后端进程，保持运行供 L4 使用
            # (移除清理代码)
            #

        # === 前端构建 ===
        if project_config.frontend:
            fe_path = (
                str(Path(project_path) / project_config.frontend.path)
                if project_config.frontend.path != "."
                else project_path
            )

            # npm install
            pkg_json = Path(fe_path) / "package.json"
            if pkg_json.exists():
                r = local.run("npm install 2>&1 | tail -5", cwd=fe_path, timeout=120)
                checks["frontend_deps"] = {
                    "status": "PASS" if r.success else "FAIL",
                    "output": r.stdout[-500:],
                }

                # build
                if project_config.frontend.build:
                    r = local.run(
                        f"{project_config.frontend.build} 2>&1 | tail -20",
                        cwd=fe_path,
                        timeout=120,
                    )
                    checks["frontend_build"] = {
                        "status": "PASS" if r.success else "FAIL",
                        "output": (r.stdout + r.stderr)[-500:],
                    }

        # === 汇总 ===
        all_pass = all(c["status"] == "PASS" for c in checks.values())
        failed = [k for k, v in checks.items() if v["status"] == "FAIL"]

        report = {
            "checks": checks,
            "all_pass": all_pass,
            "failed": failed,
        }

        # 保存报告
        report_dir = Path(__file__).parent.parent / "reports" / project_config.name
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "L3-build-report.json").write_text(json.dumps(report, indent=2))

        if all_pass:
            result.finish("PASS", report=report)
        else:
            result.finish(
                "FAIL", report=report, error=f"Failed checks: {', '.join(failed)}"
            )

        return result
