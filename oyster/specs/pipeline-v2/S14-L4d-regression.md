---
task_id: S14-L4d-regression
project: pipeline-v2
priority: 2
depends_on: [S10-qa-standards-and-skills]
modifies: ["dispatch/pipeline/layers/L4d_regression.py"]
executor: glm
---

## 目标
回归测试: 后端 pytest --cov, 前端 npm test/vitest, 新增失败检测, 页面加载时间

## 约束
- 后端优先 pytest, 前端优先 vitest/npm test
- 对比上次运行 (reports/<project>/L4d-regression-report.json)
- curl -w "%{time_total}" 检查页面加载
- 所有函数用 kwargs
- 不动任何已有文件

## 具体改动

### dispatch/pipeline/layers/L4d_regression.py

```python
#!/usr/bin/env python3
"""L4d: 回归测试 + 覆盖率 + 页面加载时间"""
import json, subprocess, sys, glob
from pathlib import Path
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
    pass

def run_frontend_tests(*, project_dir: str) -> dict:
    """
    执行前端测试:
    1. 检查 package.json 是否有 test script
    2. vitest run --reporter=json 或 npm test
    3. 解析测试结果
    返回 {"tests_run": int, "tests_passed": int, "tests_failed": int, "failures": [str]}
    """
    pass

def check_page_load_times(*, urls: list, timeout: int = 10) -> dict:
    """
    curl -w "%{time_total}" 检查每个 URL 加载时间
    返回 {"url": seconds, ...}
    """
    results = {}
    for url in urls:
        r = subprocess.run(
            ["curl", "-sf", url, "-o", "/dev/null", "-w", "%{time_total}"],
            capture_output=True, text=True, timeout=timeout
        )
        if r.returncode == 0:
            try:
                results[url] = float(r.stdout.strip())
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
        return []  # 首次运行无对比
    prev = json.loads(Path(previous_report_path).read_text())
    prev_failures = set(prev.get("all_failures", []))
    new = [f for f in current_failures if f not in prev_failures]
    return new

def run_all(*, project_dir: str, backend_path: str = None, frontend_path: str = None,
            test_urls: list = None, output_dir: str) -> dict:
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

    # 对比上次
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
```

## 验收标准
- [ ] pytest --cov 执行成功并解析覆盖率
- [ ] npm test / vitest 执行成功
- [ ] 页面加载时间检测准确 (curl -w)
- [ ] 新增失败对比逻辑正确
- [ ] L4d-regression-report.json 包含 coverage_percent, new_failures, page_load_times
- [ ] 首次运行 (无 previous report) 不报错

## 不要做
- 不要安装 pytest-cov (假设项目已有)
- 不要修改项目的测试代码
- 不要忽略页面加载时间阈值 (3s)
- 不要修改任何已有文件
