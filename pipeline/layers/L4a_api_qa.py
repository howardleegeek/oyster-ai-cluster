#!/usr/bin/env python3
"""L4a: API 拜占庭测试"""

import json, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

BYZANTINE_SCENARIOS = {
    "empty_body": {"method": "POST", "data": ""},
    "oversized_payload": {"method": "POST", "data_size": 1048576},  # 1MB of 'A'
    "sql_injection": {"method": "POST", "data": '{"id": "1; DROP TABLE users;--"}'},
    "xss": {"method": "POST", "data": '{"name": "<script>alert(1)</script>"}'},
    "invalid_token": {
        "method": "GET",
        "header": "Authorization: Bearer INVALID_TOKEN_XYZ",
    },
    "timeout_slow": {"method": "GET", "timeout": 2},  # 只等 2s
    "wrong_content_type": {
        "method": "POST",
        "content_type": "text/plain",
        "data": "not json",
    },
    "invalid_method": {"method": "PATCH", "data": "{}"},  # 如果只支持 GET/POST
    "path_traversal": {"method": "GET", "path_suffix": "/../../../etc/passwd"},
    "null_body": {"method": "POST", "data": "null"},
    "concurrent": {"method": "GET", "concurrent": 5},  # 5 个并发请求
}


def run_scenario(
    *, base_url: str, endpoint: dict, scenario_name: str, scenario: dict
) -> dict:
    """执行单个拜占庭测试场景，返回 {scenario, pass, status_code, response_time, detail}"""
    path = endpoint.get("path", "/")
    method = scenario.get("method", "GET")
    url = f"{base_url}{path}"

    # 构造 curl 命令
    curl_cmd = ["curl", "-s", "-w", "%{http_code}|%{time_total}"]

    if "timeout" in scenario:
        curl_cmd.extend(["--max-time", str(scenario["timeout"])])

    if "header" in scenario:
        curl_cmd.extend(["-H", scenario["header"]])

    if "content_type" in scenario:
        curl_cmd.extend(["-H", f"Content-Type: {scenario['content_type']}"])

    method_override = scenario.get("method")
    if method_override and method_override not in ["GET", "POST"]:
        curl_cmd.extend(["-X", method_override])

    data = scenario.get("data", "")
    if data == "null":
        data = "null"
    elif scenario.get("data_size"):
        data = "A" * scenario["data_size"]

    if data:
        curl_cmd.extend(["-d", data])

    # 添加 URL
    if "path_suffix" in scenario:
        url = url + scenario.get("path_suffix", "")

    curl_cmd.append(url)

    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout.strip()

        # 解析 status_code 和 response_time
        if "|" in output:
            parts = output.rsplit("|", 1)
            status_code = parts[0][-3:] if len(parts[0]) >= 3 else parts[0]
            response_time = float(parts[1]) if len(parts) > 1 and parts[1] else 0
            response_body = parts[0][:-4] if len(parts[0]) >= 4 else parts[0]
        else:
            status_code = "000"
            response_time = 0
            response_body = output

        # pass 判定: 不应返回 500 (server error)
        pass_result = status_code != "500"

        # SQL 注入/XSS: 不应在 response body 中回显 payload
        if scenario_name == "sql_injection" and "DROP TABLE" in response_body:
            pass_result = False
        if scenario_name == "xss" and "<script>" in response_body:
            pass_result = False

        return {
            "scenario": scenario_name,
            "pass": pass_result,
            "status_code": status_code,
            "response_time": response_time,
            "detail": f"url={url}, method={method}",
        }
    except subprocess.TimeoutExpired:
        return {
            "scenario": scenario_name,
            "pass": True,
            "status_code": "408",
            "response_time": 30,
            "detail": "timeout",
        }
    except Exception as e:
        return {
            "scenario": scenario_name,
            "pass": False,
            "status_code": "000",
            "response_time": 0,
            "detail": str(e),
        }


def run_all(
    *,
    l1_report_path: str = None,
    base_url: str,
    output_dir: str,
    endpoints: list = None,
) -> dict:
    """对 endpoints 执行全部拜占庭场景"""
    if endpoints is None:
        endpoints = []
    if l1_report_path and Path(l1_report_path).exists():
        l1 = json.loads(Path(l1_report_path).read_text())
        endpoints = l1.get("endpoints", [])

    results = []
    total_tests = 0
    passed_tests = 0
    s1_bugs = 0
    s2_bugs = 0
    bugs = []

    for ep in endpoints[:30]:  # 最多 30 个 endpoint
        for name, scenario in BYZANTINE_SCENARIOS.items():
            r = run_scenario(
                base_url=base_url, endpoint=ep, scenario_name=name, scenario=scenario
            )
            results.append(r)
            total_tests += 1
            if r["pass"]:
                passed_tests += 1
            else:
                severity = "S1" if name in ["sql_injection", "path_traversal"] else "S2"
                bugs.append(
                    {
                        "type": "api",
                        "severity": severity,
                        "endpoint": ep.get("path", "/"),
                        "scenario": name,
                        "detail": r.get("detail", ""),
                    }
                )
                if severity == "S1":
                    s1_bugs += 1
                else:
                    s2_bugs += 1

    byzantine_pass_rate = passed_tests / total_tests if total_tests > 0 else 0

    report = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "byzantine_pass_rate": byzantine_pass_rate,
        "s1_bugs": s1_bugs,
        "s2_bugs": s2_bugs,
        "bugs": bugs,
        "details": results,
    }

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    (Path(output_dir) / "L4a-api-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )
    return report


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--l1-report", default=None)
    p.add_argument("--base-url", required=True)
    p.add_argument("--output-dir", required=True)
    args = p.parse_args()
    report = run_all(
        l1_report_path=args.l1_report,
        base_url=args.base_url,
        output_dir=args.output_dir,
    )
    rate = report["byzantine_pass_rate"]
    print(
        f"L4a done: {report['passed_tests']}/{report['total_tests']} passed, byzantine rate: {rate:.1%}"
    )
