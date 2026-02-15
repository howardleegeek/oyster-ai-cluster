#!/usr/bin/env python3
"""L4: 自测层 — API + 页面 + 端到端"""

import json
import time
from pathlib import Path
from layers.base import Layer, LayerResult


class L4Test(Layer):
    name = "L4"
    max_retries = 1  # 测试不重试，失败交给 L5
    required_prev = ["L3"]

    def execute(self, project_config, prev_results: dict) -> LayerResult:
        result = LayerResult(layer=self.name, status="RUNNING")
        from executors import get_executor

        local = get_executor("local")

        project_path = str(Path(project_config.path).expanduser())
        test_results = {"api": [], "pages": [], "flows": [], "bugs": []}

        # === 启动服务 ===
        be_port = None
        fe_port = None

        if project_config.backend:
            be_path = str(Path(project_path) / project_config.backend.path)
            be_port = project_config.backend.port
            local.run(f"lsof -ti:{be_port} | xargs kill -9 2>/dev/null || true")
            time.sleep(1)
            # Use same cwd as L3 (project_path) for consistency
            local.run(
                f"nohup {project_config.backend.cmd} --port {be_port} > /tmp/pipeline-test-be-{project_config.name}.log 2>&1 &",
                cwd=project_path,
                timeout=5,
            )
            time.sleep(5)

        if project_config.frontend and project_config.frontend.serve:
            fe_path = (
                str(Path(project_path) / project_config.frontend.path)
                if project_config.frontend.path != "."
                else project_path
            )
            fe_port = project_config.frontend.port
            local.run(f"lsof -ti:{fe_port} | xargs kill -9 2>/dev/null || true")
            time.sleep(1)
            local.run(
                f"nohup {project_config.frontend.serve} -l {fe_port} > /tmp/pipeline-test-fe-{project_config.name}.log 2>&1 &",
                cwd=fe_path,
                timeout=5,
            )
            time.sleep(3)

        try:
            # === A: API 测试 ===
            if be_port:
                base = f"http://localhost:{be_port}"

                # 健康检查
                r = local.run(
                    f"curl -sf {base}{project_config.backend.health} -w '\n%{{http_code}}'",
                    timeout=10,
                )
                test_results["api"].append(
                    {
                        "endpoint": project_config.backend.health,
                        "method": "GET",
                        "test": "health",
                        "pass": r.success,
                        "response": r.stdout[-200:],
                    }
                )

                # 从 L1 report 拿 endpoints 测试
                l1 = prev_results.get("L1")
                if l1 and l1.report:
                    endpoints = l1.report.get("endpoints", [])
                    for ep in endpoints[:20]:  # 限制 20 个
                        method = ep["method"]
                        path = ep["path"]
                        if method == "GET":
                            r = local.run(
                                f"curl -sf {base}{path} -w '\n%{{http_code}}'",
                                timeout=10,
                            )
                        else:
                            r = local.run(
                                f"curl -sf -X {method} {base}{path} -H 'Content-Type: application/json' -d '{{}}' -w '\n%{{http_code}}'",
                                timeout=10,
                            )

                        passed = (
                            r.success
                            or "422" in r.stdout
                            or "401" in r.stdout
                            or "405" in r.stdout
                        )  # 422=参数校验正常, 401=需认证, 405=方法不允许
                        test_results["api"].append(
                            {
                                "endpoint": path,
                                "method": method,
                                "test": "reachable",
                                "pass": passed,
                                "response": r.stdout[-200:],
                            }
                        )
                        if not passed:
                            test_results["bugs"].append(
                                {
                                    "type": "api",
                                    "severity": "S2",
                                    "description": f"{method} {path} 返回错误",
                                    "detail": (r.stdout + r.stderr)[-300:],
                                }
                            )

            # === B: 页面测试 ===
            if fe_port and project_config.test_urls:
                for url in project_config.test_urls:
                    full_url = f"http://localhost:{fe_port}{url}"
                    r = local.run(
                        f"curl -sf {full_url} -o /dev/null -w '%{{http_code}}'",
                        timeout=10,
                    )
                    passed = r.success and "200" in r.stdout
                    test_results["pages"].append(
                        {
                            "url": url,
                            "pass": passed,
                            "status_code": r.stdout.strip(),
                        }
                    )
                    if not passed:
                        test_results["bugs"].append(
                            {
                                "type": "page",
                                "severity": "S2",
                                "description": f"页面 {url} 无法加载",
                                "detail": r.stderr[-200:],
                            }
                        )

            # === C: 流程测试 ===
            if be_port and project_config.test_flows:
                for flow in project_config.test_flows:
                    flow_name = (
                        flow.get("name", "unnamed")
                        if isinstance(flow, dict)
                        else str(flow)
                    )
                    steps = flow.get("steps", []) if isinstance(flow, dict) else []
                    flow_pass = True
                    step_results = []
                    for step in steps:
                        parts = step.split()
                        method = parts[0] if parts else "GET"
                        path = parts[1] if len(parts) > 1 else "/"
                        r = local.run(
                            f"curl -sf -X {method} http://localhost:{be_port}{path} -H 'Content-Type: application/json' -d '{{}}' -w '\n%{{http_code}}'",
                            timeout=10,
                        )
                        step_pass = r.success or "422" in r.stdout or "401" in r.stdout
                        step_results.append({"step": step, "pass": step_pass})
                        if not step_pass:
                            flow_pass = False

                    test_results["flows"].append(
                        {
                            "name": flow_name,
                            "pass": flow_pass,
                            "steps": step_results,
                        }
                    )

        finally:
            # === 清理 ===
            if be_port:
                local.run(f"lsof -ti:{be_port} | xargs kill -9 2>/dev/null || true")
            if fe_port:
                local.run(f"lsof -ti:{fe_port} | xargs kill -9 2>/dev/null || true")

        # === 汇总 ===
        api_pass = sum(1 for t in test_results["api"] if t["pass"])
        api_total = len(test_results["api"])
        page_pass = sum(1 for t in test_results["pages"] if t["pass"])
        page_total = len(test_results["pages"])
        bugs = test_results["bugs"]

        report = {
            "api": {
                "pass": api_pass,
                "total": api_total,
                "details": test_results["api"],
            },
            "pages": {
                "pass": page_pass,
                "total": page_total,
                "details": test_results["pages"],
            },
            "flows": test_results["flows"],
            "bugs": bugs,
            "bug_count": len(bugs),
            "s1_bugs": len([b for b in bugs if b["severity"] == "S1"]),
            "s2_bugs": len([b for b in bugs if b["severity"] == "S2"]),
        }

        # 保存报告
        report_dir = Path(__file__).parent.parent / "reports" / project_config.name
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "L4-test-report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False)
        )

        # 判定: 无 S1 bug 且 API/页面通过率 > 80% = PASS
        if (
            report["s1_bugs"] == 0
            and (api_total == 0 or api_pass / api_total >= 0.8)
            and (page_total == 0 or page_pass / page_total >= 0.8)
        ):
            result.finish("PASS", report=report)
        else:
            result.finish(
                "FAIL",
                report=report,
                error=f"{len(bugs)} bugs found ({report['s1_bugs']} S1, {report['s2_bugs']} S2)",
            )

        return result
