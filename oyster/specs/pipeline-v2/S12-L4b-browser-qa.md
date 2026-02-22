---
task_id: S12-L4b-browser-qa
project: pipeline-v2
priority: 2
depends_on: [S10-qa-standards-and-skills]
modifies: ["dispatch/pipeline/layers/L4b_browser_qa.py"]
executor: glm
---

## 目标
用 Playwright 实现浏览器端 QA: 页面加载检查, JS 错误捕获, 截图, E2E 流程, 响应式检查

## 约束
- 使用 playwright (已安装在 Mac-2, `python3 -m playwright` 可用)
- 如果 playwright 不可用 (GCP 节点), 优雅降级为 curl 检查并标记 skip
- 截图保存到 output_dir/screenshots/
- 从 projects.yaml 的 test_urls 读页面列表, test_flows 读 E2E 流程
- 所有函数用 kwargs
- 不动任何已有文件

## 具体改动

### dispatch/pipeline/layers/L4b_browser_qa.py

```python
#!/usr/bin/env python3
"""L4b: 浏览器 QA — Playwright 页面+E2E+响应式"""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

VIEWPORTS = [
    {"name": "desktop", "width": 1920, "height": 1080},
    {"name": "mobile",  "width": 375,  "height": 812},
]

def playwright_available() -> bool:
    """检查 playwright 是否可用"""
    try:
        r = subprocess.run(["python3", "-m", "playwright", "--version"], capture_output=True, timeout=5)
        return r.returncode == 0
    except:
        return False

def check_page(*, url: str, viewport: dict, screenshot_dir: Path) -> dict:
    """
    用 Playwright 检查单页:
    1. page.goto(url), 等待 networkidle
    2. 监听 console 'error' 事件, 统计 JS 错误数
    3. 截图保存到 screenshot_dir/<viewport_name>_<page_name>.png
    返回 {"url", "viewport", "loaded", "js_errors": int, "screenshot_path", "load_time_ms"}
    """
    # 用 subprocess 调用 playwright python script 或直接 import
    pass

def check_responsive(*, url: str, screenshot_dir: Path) -> list:
    """对同一 URL 执行两个 viewport 的检查"""
    results = []
    for vp in VIEWPORTS:
        r = check_page(url=url, viewport=vp, screenshot_dir=screenshot_dir)
        results.append(r)
    return results

def run_e2e_flow(*, flow: dict, base_url: str) -> dict:
    """
    执行 E2E 用户流程 (来自 projects.yaml test_flows)
    flow 格式: {"name": "login", "steps": ["goto /login", "fill #email user@test.com", "click button[type=submit]", "expect /dashboard"]}
    返回 {"name", "pass", "steps_detail": [...]}
    """
    pass

def run_all(*, base_url: str, test_urls: list, test_flows: list, output_dir: str) -> dict:
    """主入口"""
    screenshot_dir = Path(output_dir) / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    if not playwright_available():
        # 降级: curl 检查
        # curl -sf URL -o /dev/null -w "%{http_code}" 检查每个 URL
        report = {"skipped": True, "reason": "playwright not available", ...}
        # 写报告
        return report

    page_results = []
    total_js_errors = 0
    for url_path in test_urls:
        full_url = f"{base_url}{url_path}"
        responsive = check_responsive(url=full_url, screenshot_dir=screenshot_dir)
        for r in responsive:
            total_js_errors += r.get("js_errors", 0)
            page_results.append(r)

    e2e_results = []
    e2e_all_pass = True
    for flow in (test_flows or []):
        r = run_e2e_flow(flow=flow, base_url=base_url)
        e2e_results.append(r)
        if not r["pass"]:
            e2e_all_pass = False

    pages_loaded = sum(1 for p in page_results if p.get("loaded", False))
    pages_total = len(page_results)

    report = {
        "pages_loaded": pages_loaded,
        "pages_total": pages_total,
        "total_js_errors": total_js_errors,
        "e2e_pass": e2e_all_pass,
        "page_details": page_results,
        "e2e_details": e2e_results,
        "screenshots": [str(p) for p in screenshot_dir.glob("*.png")],
    }

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    (Path(output_dir) / "L4b-browser-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", required=True)
    p.add_argument("--test-urls", required=True, help="comma-separated URL paths")
    p.add_argument("--test-flows-json", default="[]", help="JSON string of test flows")
    p.add_argument("--output-dir", required=True)
    args = p.parse_args()
    urls = [u.strip() for u in args.test_urls.split(",") if u.strip()]
    flows = json.loads(args.test_flows_json)
    report = run_all(base_url=args.base_url, test_urls=urls, test_flows=flows, output_dir=args.output_dir)
    print(f"L4b done: {report['pages_loaded']}/{report['pages_total']} pages, {report['total_js_errors']} JS errors")
```

## 验收标准
- [ ] playwright 可用时: 每个 URL 两个 viewport 截图保存成功
- [ ] playwright 不可用时: 优雅降级为 curl 检查, report 包含 `skipped: true`
- [ ] JS 错误计数准确 (console error 事件)
- [ ] E2E 流程失败时报告具体步骤
- [ ] L4b-browser-report.json 格式正确
- [ ] screenshots/ 目录有截图文件

## 不要做
- 不要在 GCP 节点强制安装 playwright 浏览器
- 不要跳过响应式检查
- 不要修改 projects.yaml 格式
- 不要修改任何已有文件
