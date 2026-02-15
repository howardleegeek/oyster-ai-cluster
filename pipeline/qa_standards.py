#!/usr/bin/env python3
"""Pipeline v2 质量标准定义"""
import json
from pathlib import Path

API_BYZANTINE_THRESHOLD = 0.9
UI_SCORE_MIN = 70
COVERAGE_MIN = 50
PAGE_LOAD_MAX_SECONDS = 3.0
MAX_S1_BUGS = 0
MAX_S2_BUGS = 3
BROWSER_JS_ERRORS_MAX = 0
CONSECUTIVE_PASS_REQUIRED = 3

def check_api_qa(*, report: dict) -> tuple:
    """检查 API QA 报告 → (pass: bool, score: float, details: dict)"""
    total = report.get("total_tests", 0)
    passed = report.get("passed_tests", 0)
    score = (passed / total * 100) if total > 0 else 0
    byzantine_pass = report.get("byzantine_pass_rate", 0)
    ok = byzantine_pass >= API_BYZANTINE_THRESHOLD and report.get("s1_bugs", 0) == MAX_S1_BUGS
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
        report_file = None
        for fname in [f"{sub}-report.json", f"{sub}-api-report.json", f"{sub}-browser-report.json", f"{sub}-ui-report.json", f"{sub}-regression-report.json"]:
            p = rd / fname
            if p.exists():
                report_file = p
                break
        if report_file and report_file.exists():
            report = json.loads(report_file.read_text())
            ok, score, details = checker(report=report)
            results[sub] = {"pass": ok, "score": score, "details": details}
        else:
            results[sub] = {"pass": False, "score": 0, "details": {"error": f"report not found"}}

    all_pass = all(r["pass"] for r in results.values())
    avg_score = sum(r["score"] for r in results.values()) / max(len(results), 1)
    return {"project": project, "overall_pass": all_pass, "avg_score": avg_score, "sub_results": results}
