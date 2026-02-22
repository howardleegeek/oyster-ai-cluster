#!/usr/bin/env python3
"""L4d: 回归测试 + 覆盖率 + 页面加载时间"""

import json, subprocess, sys, glob
from pathlib import Path
from typing import Optional, List

sys.path.insert(0, str(Path(__file__).parent.parent))


def run_backend_tests(*, project_dir: str) -> dict:
    """执行后端测试"""
    pd = Path(project_dir)
    if not pd.exists():
        return {
            "coverage_percent": 0,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": [],
        }

    # 检查 pytest 是否可用
    pytest_check = subprocess.run(["which", "pytest"], capture_output=True)
    if pytest_check.returncode != 0:
        # 检查是否有 test_*.py 文件
        test_files = list(pd.glob("test_*.py")) + list(pd.glob("tests/*.py"))
        if not test_files:
            return {
                "coverage_percent": 0,
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "failures": [],
                "note": "no pytest or test files",
            }
        return {
            "coverage_percent": 0,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": [],
            "note": "pytest not available",
        }

    # 运行 pytest with coverage
    try:
        result = subprocess.run(
            ["pytest", "--cov=.", "--cov-report=json", "-v", "--tb=short", str(pd)],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(pd),
        )

        # 解析覆盖率
        coverage_json = pd / "coverage.json"
        coverage_percent = 0
        if coverage_json.exists():
            try:
                cov_data = json.loads(coverage_json.read_text())
                coverage_percent = cov_data.get("totals", {}).get("percent_covered", 0)
            except:
                pass

        # 解析测试结果
        output = result.stdout
        tests_run = 0
        tests_passed = 0
        tests_failed = 0
        failures = []

        # 简单解析
        if "passed" in output:
            tests_passed = output.count(" PASSED")
        if "failed" in output:
            tests_failed = output.count(" FAILED")
        tests_run = tests_passed + tests_failed

        return {
            "coverage_percent": coverage_percent,
            "tests_run": tests_run,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "failures": failures,
        }
    except subprocess.TimeoutExpired:
        return {
            "coverage_percent": 0,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": ["test timeout"],
        }
    except Exception as e:
        return {
            "coverage_percent": 0,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": [str(e)],
        }


def run_frontend_tests(*, project_dir: str) -> dict:
    """执行前端测试"""
    pd = Path(project_dir)
    if not pd.exists():
        return {"tests_run": 0, "tests_passed": 0, "tests_failed": 0, "failures": []}

    # 检查 package.json
    pkg_json = pd / "package.json"
    if not pkg_json.exists():
        return {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": [],
            "note": "no package.json",
        }

    # 检查是否有 vitest 或 npm test
    vitest_check = subprocess.run(["which", "vitest"], capture_output=True)
    npm_test_check = subprocess.run(
        ["npm", "test", "--dry-run"], capture_output=True, cwd=str(pd), timeout=10
    )

    if vitest_check.returncode == 0:
        try:
            result = subprocess.run(
                ["vitest", "run", "--reporter=json"],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(pd),
            )
            # 解析结果
            return {
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "failures": [],
                "note": "vitest not fully parsed",
            }
        except:
            pass

    # 尝试 npm test
    if npm_test_check.returncode == 0:
        try:
            result = subprocess.run(
                ["npm", "test", "--", "--watchAll=false"],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(pd),
            )
            return {
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "failures": [],
                "note": "npm test run",
            }
        except:
            pass

    return {
        "tests_run": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "failures": [],
        "note": "no test runner",
    }


def check_page_load_times(*, urls: list, timeout: int = 10) -> dict:
    """curl -w "%{time_total}" 检查每个 URL 加载时间"""
    results = {}
    for url in urls:
        try:
            r = subprocess.run(
                ["curl", "-sf", url, "-o", "/dev/null", "-w", "%{time_total}"],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if r.returncode == 0:
                try:
                    results[url] = float(r.stdout.strip())
                except ValueError:
                    results[url] = 999.0
            else:
                results[url] = 999.0
        except subprocess.TimeoutExpired:
            results[url] = 999.0
        except:
            results[url] = 999.0
    return results


def compare_with_previous(*, current_failures: list, previous_report_path: str) -> list:
    """对比上次运行，找出新增失败测试"""
    if not Path(previous_report_path).exists():
        return []  # 首次运行无对比
    try:
        prev = json.loads(Path(previous_report_path).read_text())
        prev_failures = set(prev.get("all_failures", []))
        new = [f for f in current_failures if f not in prev_failures]
        return new
    except:
        return []


def run_all(
    *,
    project_dir: str,
    backend_path: str = None,
    frontend_path: str = None,
    test_urls: list = None,
    output_dir: str = None,
) -> dict:
    """主入口"""
    if test_urls is None:
        test_urls = []
    if output_dir is None:
        output_dir = "."

    backend_result = {}
    frontend_result = {}
    all_failures = []

    if backend_path:
        backend_result = run_backend_tests(
            project_dir=str(Path(project_dir) / backend_path)
        )
        all_failures.extend(backend_result.get("failures", []))

    if frontend_path:
        frontend_result = run_frontend_tests(
            project_dir=str(Path(project_dir) / frontend_path)
        )
        all_failures.extend(frontend_result.get("failures", []))

    page_load_times = check_page_load_times(urls=test_urls)

    # 对比上次
    prev_path = Path(output_dir) / "L4d-regression-report.json"
    new_failures = compare_with_previous(
        current_failures=all_failures, previous_report_path=str(prev_path)
    )

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
    (Path(output_dir) / "L4d-regression-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )
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
    report = run_all(
        project_dir=args.project_dir,
        backend_path=args.backend_path,
        frontend_path=args.frontend_path,
        test_urls=urls,
        output_dir=args.output_dir,
    )
    print(
        f"L4d done: coverage={report['coverage_percent']}%, new_failures={len(report['new_failures'])}"
    )
