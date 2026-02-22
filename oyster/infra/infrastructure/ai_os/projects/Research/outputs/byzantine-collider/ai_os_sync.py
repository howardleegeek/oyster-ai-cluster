#!/usr/bin/env python3
"""
拜占庭对撞器 - 自动保存到 ai_os
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional


# 默认 ai_os 路径
DEFAULT_AI_OS_PATH = (
    Path.home()
    / "Downloads"
    / "infrastructure"
    / "ai_os"
    / "projects"
    / "Research"
    / "outputs"
    / "byzantine-collider"
)


def save_to_ai_os(collision_data: dict, ai_os_path: Optional[str] = None) -> str:
    """
    自动保存碰撞结果到 ai_os

    Args:
        collision_data: 碰撞数据
        ai_os_path: ai_os 目录路径

    Returns:
        保存的文件路径
    """

    target_dir = Path(ai_os_path) if ai_os_path else DEFAULT_AI_OS_PATH

    # 确保目录存在
    target_dir.mkdir(parents=True, exist_ok=True)

    # 生成文件名
    timestamp = collision_data.get("created_at", datetime.now().isoformat())
    topic = collision_data.get("topic", "unknown")
    collision_id = collision_data.get(
        "id", timestamp.replace(":", "-").replace(".", "-")
    )

    # 清理 topic 用于文件名
    safe_topic = "".join(c for c in topic if c.isalnum() or c in " -_").strip()[:30]
    filename = f"{collision_id}_{safe_topic}.json"

    file_path = target_dir / filename

    # 保存 JSON
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(collision_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 已保存到 ai_os: {file_path}")

    # 同时生成 Markdown 报告
    try:
        from reporter import generate_collision_report

        md_path = target_dir / f"{collision_id}_{safe_topic}.md"
        generate_collision_report(collision_data, str(target_dir))
    except Exception as e:
        print(f"⚠️ Markdown 生成失败: {e}")

    # 更新 README 索引
    update_readme_index(target_dir, collision_data)

    return str(file_path)


def update_readme_index(target_dir: Path, collision_data: dict):
    """更新 README 索引"""

    readme_path = target_dir / "README.md"

    # 读取现有 README
    existing_content = ""
    if readme_path.exists():
        existing_content = readme_path.read_text(encoding="utf-8")

    # 提取现有内容（如果有）
    lines = existing_content.split("\n") if existing_content else []

    # 找到碰撞记录表格的位置
    table_start = -1
    table_end = -1
    for i, line in enumerate(lines):
        if "| ID | 主题" in line:
            table_start = i
        if table_start > 0 and table_end < 0 and line.startswith("---"):
            table_end = i
            break

    # 生成新条目
    collision_id = collision_data.get("id", "unknown")
    topic = collision_data.get("topic", "未知主题")
    timestamp = collision_data.get("created_at", "")[:10]

    new_entry = f"| {collision_id} | {topic} | {timestamp} | ✅ 完成 |"

    # 构建新内容
    if table_start > 0 and table_end > 0:
        # 插入新条目（在表头之后）
        lines.insert(table_end + 1, new_entry)
        new_content = "\n".join(lines)
    else:
        # 创建新 README
        new_content = f"""# 拜占庭对撞记录

| ID | 主题 | 日期 | 状态 |
|----|------|------|------|
{new_entry}

---
*自动生成*
"""

    readme_path.write_text(new_content, encoding="utf-8")
    print(f"📝 已更新索引: {readme_path}")


def sync_to_ai_os(ai_os_path: Optional[str] = None) -> int:
    """
    同步本地数据到 ai_os

    Returns:
        同步的文件数量
    """

    target_dir = Path(ai_os_path) if ai_os_path else DEFAULT_AI_OS_PATH
    source_dir = Path("./data")

    if not source_dir.exists():
        print("📁 无本地数据需要同步")
        return 0

    count = 0
    for json_file in source_dir.glob("*.json"):
        target_file = target_dir / json_file.name
        if not target_file.exists():
            shutil.copy2(json_file, target_file)
            count += 1
            print(f"📤 同步: {json_file.name}")

    print(f"✅ 同步完成: {count} 个文件")
    return count


if __name__ == "__main__":
    # 测试
    test_data = {
        "id": "test-001",
        "topic": "测试主题",
        "rounds": 2,
        "created_at": datetime.now().isoformat(),
        "status": "completed",
    }

    save_to_ai_os(test_data)
