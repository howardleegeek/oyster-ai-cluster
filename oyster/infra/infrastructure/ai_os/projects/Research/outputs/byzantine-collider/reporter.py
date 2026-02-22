#!/usr/bin/env python3
"""
拜占庭对撞器 - 碰撞报告自动生成
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def generate_collision_report(
    collision_data: dict, output_dir: Optional[str] = None
) -> str:
    """
    生成碰撞报告 Markdown

    Args:
        collision_data: 碰撞数据
        output_dir: 输出目录

    Returns:
        Markdown 内容
    """

    topic = collision_data.get("topic", "未知主题")
    rounds = collision_data.get("rounds", 0)
    llm = collision_data.get("llm", "unknown")
    result = collision_data.get("result", {})
    timestamp = collision_data.get("created_at", datetime.now().isoformat())

    # 生成 ID
    collision_id = collision_data.get(
        "id", timestamp.replace(":", "-").replace(".", "-")
    )

    md = []
    md.append(f"# 拜占庭对撞报告 - {collision_id}")
    md.append("")
    md.append(f"**主题**: {topic}")
    md.append(f"**时间**: {timestamp}")
    md.append(f"**轮次**: {rounds}")
    md.append(f"**模型**: {llm}")
    md.append("")
    md.append("---")
    md.append("")

    # 碰撞历史
    history = result.get("history", [])
    if history:
        md.append("## 碰撞过程")
        md.append("")

        for i, round_data in enumerate(history, 1):
            md.append(f"### 第 {i} 轮")
            md.append("")

            challenger = round_data.get("challenger", "").strip()
            defender = round_data.get("defender", "").strip()

            if challenger:
                md.append("**挑战者**")
                md.append("")
                md.append(challenger)
                md.append("")

            if defender:
                md.append("**辩护者**")
                md.append("")
                md.append(defender)
                md.append("")

            md.append("---")
            md.append("")

    # 收敛结论
    convergence = result.get("convergence", {})
    if convergence:
        summary = convergence.get("summary", "").strip()
        if summary:
            md.append("## 收敛结论")
            md.append("")
            md.append(summary)
            md.append("")

    # 碰撞元数据
    status = collision_data.get("status", "unknown")
    md.append("---")
    md.append("")
    md.append(f"*报告生成时间: {datetime.now().isoformat()}*")
    md.append(f"*状态: {status}*")

    content = "\n".join(md)

    # 保存到文件
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        filename = f"{collision_id}.md"
        file_path = output_path / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"📄 报告已保存: {file_path}")

    return content


def generate_research_report(
    research_data: dict, output_dir: Optional[str] = None
) -> str:
    """生成调研报告"""

    query = research_data.get("query", "未知查询")
    report = research_data.get("report", {})
    timestamp = research_data.get("timestamp", datetime.now().isoformat())

    md = []
    md.append(f"# 网络调研报告")
    md.append("")
    md.append(f"**查询**: {query}")
    md.append(f"**时间**: {timestamp}")
    md.append("")
    md.append("---")
    md.append("")

    # 事实
    facts = report.get("facts", [])
    if facts:
        md.append("## 确认事实")
        md.append("")
        for i, fact in enumerate(facts, 1):
            md.append(f"### {i}. {fact.get('content', '')[:100]}...")
            md.append(f"   - 置信度: {fact.get('confidence', 0):.0%}")
            md.append("")

    # 争议事实
    disputed = report.get("disputed_facts", [])
    if disputed:
        md.append("## 争议事实")
        md.append("")
        for i, fact in enumerate(disputed, 1):
            md.append(f"### {i}. {fact.get('content', '')[:100]}...")
            md.append("")

    content = "\n".join(md)

    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        filename = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        file_path = output_path / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"📄 调研报告已保存: {file_path}")

    return content


if __name__ == "__main__":
    # 测试
    test_data = {
        "id": "test-001",
        "topic": "测试主题",
        "rounds": 2,
        "llm": "zhipu",
        "created_at": datetime.now().isoformat(),
        "status": "completed",
        "result": {
            "history": [
                {"challenger": "这是挑战者的质疑...", "defender": "这是辩护者的回应..."}
            ],
            "convergence": {"summary": "这是收敛结论..."},
        },
    }

    print(generate_collision_report(test_data))
