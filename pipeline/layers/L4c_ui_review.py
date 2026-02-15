#!/usr/bin/env python3
"""L4c: UI 质量评审 — LLM 评分 + 溢出检测"""

import json, subprocess, sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

MM_CLI = Path.home() / "Downloads" / "dispatch" / "mm"


def call_mm_review(*, html_snippet: str, page_url: str) -> dict:
    """调用 mm CLI 评分 UI 质量"""
    # 检查 mm CLI 是否存在
    if not MM_CLI.exists():
        return {
            "visual": 0,
            "layout": 0,
            "readability": 0,
            "professional": 0,
            "total_score": 0,
            "issues": ["mm CLI not found"],
        }

    prompt = f"""分析以下网页 HTML 的 UI 质量。评分维度: 视觉(25分), 布局(25分), 可读性(25分), 专业度(25分)。
输出 JSON: {{visual, layout, readability, professional, total_score, issues: [字符串]}}
HTML: {html_snippet[:2000]}"""

    try:
        result = subprocess.run(
            [str(MM_CLI), prompt], capture_output=True, text=True, timeout=60
        )
        output = result.stdout.strip()

        # 尝试解析 JSON
        try:
            score_data = json.loads(output)
            return score_data
        except json.JSONDecodeError:
            return {
                "visual": 0,
                "layout": 0,
                "readability": 0,
                "professional": 0,
                "total_score": 0,
                "issues": ["failed to parse mm response"],
            }
    except Exception as e:
        return {
            "visual": 0,
            "layout": 0,
            "readability": 0,
            "professional": 0,
            "total_score": 0,
            "issues": [str(e)],
        }


def detect_overflow(*, page_url: str) -> dict:
    """检测布局溢出 (简化版 - 用 curl)"""
    try:
        # 用 curl 获取页面，检查是否有明显的布局问题
        result = subprocess.run(
            ["curl", "-sf", page_url], capture_output=True, text=True, timeout=10
        )
        html = result.stdout

        # 简单检查: 是否有明显的溢出相关 CSS
        has_overflow = "overflow:" in html or "overflow-x:" in html

        return {"has_overflow": has_overflow, "note": "simplified check"}
    except:
        return {"has_overflow": False, "note": "check failed"}


def get_page_html(*, url: str) -> str:
    """curl 获取页面 HTML (前 5000 字符)"""
    try:
        r = subprocess.run(
            ["curl", "-sf", url], capture_output=True, text=True, timeout=10
        )
        return r.stdout[:5000] if r.returncode == 0 else ""
    except:
        return ""


def run_all(*, l4b_report_path: str = None, base_url: str, output_dir: str) -> dict:
    """主入口: 读 L4b 报告获取页面列表，逐个评分"""
    pages = []

    if l4b_report_path and Path(l4b_report_path).exists():
        l4b = json.loads(Path(l4b_report_path).read_text())
        # 从 L4b 报告提取唯一 URL 列表
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
            score = {
                "visual": 0,
                "layout": 0,
                "readability": 0,
                "professional": 0,
                "total_score": 0,
                "issues": ["page unreachable"],
            }

        overflow = detect_overflow(page_url=url)

        results.append(
            {**score, "url": url, "has_overflow": overflow.get("has_overflow", False)}
        )

    report = {"pages": results}
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    (Path(output_dir) / "L4c-ui-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )
    return report


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--l4b-report", default=None)
    p.add_argument("--base-url", required=True)
    p.add_argument("--output-dir", required=True)
    args = p.parse_args()
    report = run_all(
        l4b_report_path=args.l4b_report,
        base_url=args.base_url,
        output_dir=args.output_dir,
    )
    scores = [p["total_score"] for p in report.get("pages", [])]
    avg = sum(scores) / len(scores) if scores else 0
    print(f"L4c done: {len(scores)} pages, avg score: {avg:.0f}/100")
