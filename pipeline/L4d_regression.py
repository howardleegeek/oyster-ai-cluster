#!/usr/bin/env python3
"""L4d: 回归测试 + 覆盖率 + 页面加载时间"""
import json, subprocess, sys, glob, os
from pathlib import Path
from typing import Optional, List
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_backend_tests(*, project_dir: str) -> dict:
    """
    执行后端测试:
    1. 检查 pytest 是否可用
    2. pytest --cov=. --cov-report=json -v --tb=short
    3. 解析 coverage.json 获取覆盖率
    4. 如果无 pytest，检查 test_*.py 文件是否存在
    返回 {"coverage_percent": float, "tests_run": int, "tests_passed": int, "tests_failed": int, "failures": [str]}
    """
    result = {
        "coverage_percent": 0.0,
        "tests_run": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "failures": []
    }

    project_path = Path(project_dir)
    if not project_path.exists():
        return result

    has_pytest = subprocess.run(
        ["python3", "-c", "import pytest"],
        capture_output=True
    ).returncode == 0

    if not has_pytest:
        test_files = list(project_path.glob("test_*.py")) + list(project_path.glob("**/test_*.py"))
        if test_files:
            result["failures"].append("pytest not available but test files exist")
        return result

    coverage_dir = project_path / ".coverage_json"
    coverage_dir.mkdir(exist_ok=True)

    cov_args = ["--cov=. ", "--cov-report=json", "-v", "--tb=short"]
    cmd = ["pytest"] + cov_args

    r = subprocess.run(
        cmd,
        cwd=str(project_path),
        capture_output=True,
        text=True,
        timeout=300
    )

    output = r.stdout + r.stderr

    test_files = list(project_path.glob("test_*.py")) + list(project_path.glob("**/test_*.py"))
    result["tests_run"] = len(test_files)

    for line in output.split("\n"):
        if "passed" in line.lower():
            parts = line.split()
            for i, p in enumerate(parts):
                if p == "passed":
                    try:
                        result["tests_passed"] = int(parts[i-1])
                    except (ValueError, IndexError):
                        pass
        if "failed" in line.lower():
            parts = line.split()
            for i, p in enumerate(parts):
                if p == "failed":
                    try:
                        result["tests_failed"] = int(parts[i-1])
                    except (ValueError, IndexError):
                        pass

    coverage_file = project_path / ".coverage_json" / "coverage.json"
    if coverage_file.exists():
        try:
            cov_data = json.loads(coverage_file.read_text())
            totals = cov_data.get("totals", {})
            result["coverage_percent"] = round(totals.get("percent_covered", 0), 2)
        except (json.JSONDecodeError, KeyError):
            pass

    for line in output.split("\n"):
        if "FAILED" in line or "ERROR" in line:
            result["failures"].append(line.strip())

    if r.returncode != 0 and not result["failures"]:
        result["failures"].append(f"pytest exited with code {r.returncode}")

    return result


def run_frontend_tests(*, project_dir: str) -> dict:
    """
    执行前端测试:
    1. 检查 package.json 是否有 test script
    2. vitest run --reporter=json 或 npm test
    3. 解析测试结果
    返回 {"tests_run": int, "tests_passed": int, "tests_failed": int, "failures": [str]}
    """
    result = {
        "tests_run": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "failures": []
    }

    project_path = Path(project_dir)
    if not project_path.exists():
        return result

    pkg_json = project_path / "package.json"
    if not pkg_json.exists():
        return result

    try:
        pkg = json.loads(pkg_json.read_text())
        scripts = pkg.get("scripts", {})
    except (json.JSONDecodeError, FileNotFoundError):
        return result

    has_vitest = "vitest" in scripts.get("test", "") or subprocess.run(
        ["which", "vitest"], capture_output=True
    ).returncode == 0

    if has_vitest:
        r = subprocess.run(
            ["vitest", "run", "--reporter=json"],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=300
        )
        output = r.stdout + r.stderr

        try:
            for line in output.split("\n"):
                if line.startswith("{"):
                    data = json.loads(line)
                    if data.get("type") == "test":
                        result["tests_run"] = data.get("testResults", [{}])[0].get("assertionResults", [])
        except (json.JSONDecodeError, ValueError):
            pass

        if "passed" in output.lower():
            import re
            m = re.search(r"(\d+)\s+passed", output)
            if m:
                result["tests_passed"] = int(m.group(1))
        if "failed" in output.lower():
            import re
            m = re.search(r"(\d+)\s+failed", output)
            if m:
                result["tests_failed"] = int(m.group(1))

    else:
        r = subprocess.run(
            ["npm", "test", "--", "--coverage=false"],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=300
        )
        output = r.stdout + r.stderr

        import re
        m = re.search(r"(\d+)\s+Tests?:\s+(\d+)\s+passed", output)
        if m:
            result["tests_passed"] = int(m.group(2))
        m = re.search(r"(\d+)\s+Tests?:\s+(\d+)\s+failed", output)
        if m:
            result["tests_failed"] = int(m.group(2))

        result["tests_run"] = result["tests_passed"] + result["tests_failed"]

    for line in output.split("\n"):
        if "FAIL" in line or "Error:" in line:
            result["failures"].append(line.strip())

    return result


def check_page_load_times(*, urls: list, timeout: int = 10) -> dict:
    """
    curl -w "%{time_total}" 检查每个 URL 加载时间
    返回 {"url": seconds, ...}
    """
    results = {}
    for url in urls:
        r = subprocess.run(
            ["curl", "-sf", url, "-o", "/dev/null", "-w", "%{time_total}"],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if r.returncode == 0:
            try:
                results[url] = round(float(r.stdout.strip()), 3)
            except ValueError:
                results[url] = 999.0
        else:
            results[url] = 999.0
    return results


def compare_with_previous(*, current_failures: list, previous_report_path: str) -> list:
    """
    对比上次运行，找出新增失败测试
    返回 new_failures 列表
    """
    if not Path(previous_report_path).exists():
        return []
    try:
        prev = json.loads(Path(previous_report_path).read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        return []
    prev_failures = set(prev.get("all_failures", []))
    new = [f for f in current_failures if f not in prev_failures]
    return new


def run_all(*, project_dir: str, backend_path: Optional[str] = None, frontend_path: Optional[str] = None,
            test_urls: Optional[List[str]] = None, output_dir: str) -> dict:
    """主入口"""
    backend_result = {}
    frontend_result = {}
    all_failures = []

    if backend_path:
        backend_result = run_backend_tests(project_dir=str(Path(project_dir) / backend_path))
        all_failures.extend(backend_result.get("failures", []))

    if frontend_path:
        frontend_result = run_frontend_tests(project_dir=str(Path(project_dir) / frontend_path))
        all_failures.extend(frontend_result.get("failures", []))

    page_load_times = check_page_load_times(urls=test_urls or [])

    prev_path = Path(output_dir) / "L4d-regression-report.json"
    new_failures = compare_with_previous(current_failures=all_failures, previous_report_path=str(prev_path))

    coverage = backend_result.get("coverage_percent", 0)

    report = {
        "coverage_percent": coverage,
        "backend": backend_result,
        "frontend": frontend_result,
        "page_load_times": page_load_times,
        "all_failures": all_failures,
        "new_failures": new_failures,
    }

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    (Path(output_dir) / "L4d-regression-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--project-dir", required=True)
    p.add_argument("--backend-path", default=None)
    p.add_argument("--frontend-path", default=None)
    p.add_argument("--test-urls", default="", help="comma-separated URLs")
    p.add_argument("--output-dir", required=True)
    args = p.parse_args()
    urls = [u.strip() for u in args.test_urls.split(",") if u.strip()]
    report = run_all(project_dir=args.project_dir, backend_path=args.backend_path,
                     frontend_path=args.frontend_path, test_urls=urls, output_dir=args.output_dir)
    print(f"L4d done: coverage={report['coverage_percent']}%, new_failures={len(report['new_failures'])}")
