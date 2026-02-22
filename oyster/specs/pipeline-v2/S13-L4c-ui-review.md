---
task_id: S13-L4c-ui-review
project: pipeline-v2
priority: 3
depends_on: [S12-L4b-browser-qa]
modifies: ["dispatch/pipeline/layers/L4c_ui_review.py"]
executor: glm
---

## 目标
用 MiniMax LLM (mm CLI) 对 L4b 截图进行 UI 质量评分 + Playwright 检测布局溢出

## 约束
- 调用 mm CLI: `python3 ~/Downloads/dispatch/mm "prompt"` (MiniMax API, 免费无限)
- mm CLI 不支持图片输入，所以 UI 评分基于页面 HTML 结构分析，不是截图
- 布局溢出用 Playwright JS 注入: `document.body.scrollWidth > window.innerWidth`
- 如果 mm/playwright 都不可用，整层标记 skip
- 所有函数用 kwargs
- 不动任何已有文件

## 具体改动

### dispatch/pipeline/layers/L4c_ui_review.py

```python
#!/usr/bin/env python3
"""L4c: UI 质量评审 — LLM 评分 + 溢出检测"""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

MM_CLI = Path.home() / "Downloads" / "dispatch" / "mm"

def call_mm_review(*, html_snippet: str, page_url: str) -> dict:
    """
    调用 mm CLI 评分 UI 质量
    返回 {"visual": 0-25, "layout": 0-25, "readability": 0-25, "professional": 0-25, "total_score": 0-100, "issues": [...]}

    Prompt 模板:
    "分析以下网页 HTML 的 UI 质量。评分维度: 视觉(25分), 布局(25分), 可读性(25分), 专业度(25分)。
     输出 JSON: {visual, layout, readability, professional, total_score, issues: [字符串]}
     HTML: ..."
    """
    pass

def detect_overflow(*, page_url: str) -> dict:
    """
    Playwright JS 注入检测布局溢出
    返回 {"has_overflow": bool, "scroll_width": int, "client_width": int}

    JS: document.body.scrollWidth > document.documentElement.clientWidth
    """
    pass

def get_page_html(*, url: str) -> str:
    """curl 获取页面 HTML (前 5000 字符)"""
    r = subprocess.run(["curl", "-sf", url], capture_output=True, text=True, timeout=10)
    return r.stdout[:5000] if r.returncode == 0 else ""

def run_all(*, l4b_report_path: str, base_url: str, output_dir: str) -> dict:
    """主入口: 读 L4b 报告获取页面列表，逐个评分"""
    l4b = json.loads(Path(l4b_report_path).read_text()) if Path(l4b_report_path).exists() else {}

    # 从 L4b 报告提取唯一 URL 列表
    pages = []
    seen_urls = set()
    for detail in l4b.get("page_details", []):
        url = detail.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            pages.append(url)

    if not pages and base_url:
        pages = [base_url]  # 至少检查首页

    results = []
    for url in pages:
        html = get_page_html(url=url)
        if html:
            score = call_mm_review(html_snippet=html, page_url=url)
        else:
            score = {"visual": 0, "layout": 0, "readability": 0, "professional": 0, "total_score": 0, "issues": ["page unreachable"]}

        overflow = detect_overflow(page_url=url) if playwright_available() else {"has_overflow": False, "note": "playwright not available"}

        results.append({**score, "url": url, "has_overflow": overflow.get("has_overflow", False)})

    report = {"pages": results}
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    (Path(output_dir) / "L4c-ui-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--l4b-report", required=True)
    p.add_argument("--base-url", required=True)
    p.add_argument("--output-dir", required=True)
    args = p.parse_args()
    report = run_all(l4b_report_path=args.l4b_report, base_url=args.base_url, output_dir=args.output_dir)
    scores = [p["total_score"] for p in report.get("pages", [])]
    avg = sum(scores) / len(scores) if scores else 0
    print(f"L4c done: {len(scores)} pages, avg score: {avg:.0f}/100")
```

## 验收标准
- [ ] mm CLI 调用成功，返回 4 维度评分 JSON
- [ ] 布局溢出检测 JS 注入正确
- [ ] mm 不可用时优雅降级，不崩溃
- [ ] L4c-ui-report.json 包含 pages 数组，每个 page 有 total_score 和 has_overflow
- [ ] 所有函数用 kwargs

## 不要做
- 不要用 OpenAI/Claude API (只用 mm CLI)
- 不要发送截图到 API (mm 不支持图片)
- 不要修改 L4b 报告
- 不要修改任何已有文件
