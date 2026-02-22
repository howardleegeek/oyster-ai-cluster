---
task_id: S11-L4a-api-qa
project: pipeline-v2
priority: 2
depends_on: [S10-qa-standards-and-skills]
modifies: ["dispatch/pipeline/layers/L4a_api_qa.py"]
executor: glm
---

## 目标
实现拜占庭矩阵 API 测试 — 对每个 endpoint 执行 11 种异常攻击场景，输出 L4a-api-report.json

## 约束
- 只用 subprocess + curl，不引入 requests/httpx
- 从 L1 report 的 endpoints 字段读取 API 列表
- 所有函数用 kwargs
- 不动任何已有文件

## 具体改动

### dispatch/pipeline/layers/L4a_api_qa.py

```python
#!/usr/bin/env python3
"""L4a: API 拜占庭测试"""
import json, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

BYZANTINE_SCENARIOS = {
    "empty_body":       {"method": "POST", "data": ""},
    "oversized_payload":{"method": "POST", "data_size": 1048576},  # 1MB of 'A'
    "sql_injection":    {"method": "POST", "data": '{"id": "1; DROP TABLE users;--"}'},
    "xss":              {"method": "POST", "data": '{"name": "<script>alert(1)</script>"}'},
    "invalid_token":    {"method": "GET",  "header": "Authorization: Bearer INVALID_TOKEN_XYZ"},
    "timeout_slow":     {"method": "GET",  "timeout": 2},  # 只等 2s
    "wrong_content_type":{"method": "POST","content_type": "text/plain", "data": "not json"},
    "invalid_method":   {"method": "PATCH","data": "{}"},  # 如果只支持 GET/POST
    "path_traversal":   {"method": "GET",  "path_suffix": "/../../../etc/passwd"},
    "null_body":        {"method": "POST", "data": "null"},
    "concurrent":       {"method": "GET",  "concurrent": 5},  # 5 个并发请求
}

def run_scenario(*, base_url: str, endpoint: dict, scenario_name: str, scenario: dict) -> dict:
    """执行单个拜占庭测试场景，返回 {scenario, pass, status_code, response_time, detail}"""
    path = endpoint["path"]
    method = scenario.get("method", "GET")
    url = f"{base_url}{path}"

    # 构造 curl 命令
    # ... (根据 scenario 类型构造不同 curl 参数)
    # curl -s -o /dev/null -w "%{http_code}|%{time_total}" -X METHOD URL ...
    # pass 判定: 不应返回 500 (server error)
    # SQL 注入/XSS: 不应在 response body 中回显 payload
    # 返回结构化结果
    pass

def run_all(*, l1_report_path: str, base_url: str, output_dir: str) -> dict:
    """对 L1 report 中所有 endpoints 执行全部拜占庭场景"""
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
            r = run_scenario(base_url=base_url, endpoint=ep, scenario_name=name, scenario=scenario)
            results.append(r)
            total_tests += 1
            if r["pass"]:
                passed_tests += 1
            else:
                severity = "S1" if name in ["sql_injection", "path_traversal"] else "S2"
                bugs.append({"type": "api", "severity": severity, "endpoint": ep["path"], "scenario": name, "detail": r.get("detail", "")})
                if severity == "S1": s1_bugs += 1
                else: s2_bugs += 1

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
    (Path(output_dir) / "L4a-api-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--l1-report", required=True)
    p.add_argument("--base-url", required=True)
    p.add_argument("--output-dir", required=True)
    args = p.parse_args()
    report = run_all(l1_report_path=args.l1_report, base_url=args.base_url, output_dir=args.output_dir)
    rate = report["byzantine_pass_rate"]
    print(f"L4a done: {report['passed_tests']}/{report['total_tests']} passed, byzantine rate: {rate:.1%}")
```

## 验收标准
- [ ] 11 个拜占庭场景全部实现 (empty_body, oversized, sql_injection, xss, invalid_token, timeout, wrong_content_type, invalid_method, path_traversal, null_body, concurrent)
- [ ] `python3 layers/L4a_api_qa.py --l1-report test_l1.json --base-url http://localhost:8000 --output-dir /tmp/test` 产出 L4a-api-report.json
- [ ] SQL 注入/路径遍历标记为 S1 severity
- [ ] 只用 curl + subprocess，无 requests 依赖
- [ ] report 包含 byzantine_pass_rate 字段

## 不要做
- 不要安装 requests/httpx
- 不要修改 L1 report 格式
- 不要修改其他层的代码
- 不要跳过任何拜占庭场景
