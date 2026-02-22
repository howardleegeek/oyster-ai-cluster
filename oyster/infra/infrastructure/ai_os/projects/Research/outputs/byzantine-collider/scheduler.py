#!/usr/bin/env python3
"""
拜占庭对撞器 - 定时任务调度
"""

import os
import schedule
import time
import json
from datetime import datetime
from pathlib import Path

# 导入模块
try:
    from storage import init_db, list_collisions, get_collision
    from ai_os_sync import sync_to_ai_os
    from notify import notifier
    from reporter import generate_collision_report
except ImportError:
    print("⚠️ 部分模块未导入")


def daily_report():
    """每日报告任务"""
    print("\n📊 生成每日报告...")

    try:
        # 获取今日碰撞
        today = datetime.now().date()
        collisions = list_collisions(limit=100)

        today_collisions = [
            c for c in collisions if c.get("created_at", "").startswith(str(today))
        ]

        if today_collisions:
            print(f"今日碰撞: {len(today_collisions)} 次")

            # 生成报告
            for c in today_collisions[:5]:  # 只处理最近5个
                collision = get_collision(c["id"])
                if collision and collision.get("result"):
                    generate_collision_report(collision)
        else:
            print("今日无碰撞")

    except Exception as e:
        print(f"❌ 报告生成失败: {e}")


def sync_to_cloud():
    """同步到 ai_os"""
    print("\n🔄 同步到 ai_os...")

    try:
        count = sync_to_ai_os()
        print(f"✅ 同步完成: {count} 个文件")
    except Exception as e:
        print(f"❌ 同步失败: {e}")


def health_check():
    """健康检查"""
    print("\n❤️ 健康检查...")

    try:
        from storage import init_db

        init_db()
        print("✅ 数据库连接正常")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")


def weekly_summary():
    """每周摘要"""
    print("\n📅 生成每周摘要...")

    try:
        collisions = list_collisions(limit=100)

        # 统计
        total = len(collisions)
        completed = sum(1 for c in collisions if c.get("status") == "completed")

        summary = f"""
📊 拜占庭对撞器周报

总计碰撞: {total} 次
完成: {completed} 次
成功率: {completed / total * 100:.1f}% (如果有数据)
"""
        print(summary)

        # 发送通知
        if notifier.telegram_token:
            notifier.notify("周报摘要", summary)

    except Exception as e:
        print(f"❌ 周报生成失败: {e}")


def setup_schedule():
    """设置定时任务"""

    # 每日任务
    schedule.every().day.at("09:00").do(daily_report)  # 每日报告
    schedule.every().day.at("23:00").do(sync_to_cloud)  # 每日同步

    # 健康检查（每小时）
    schedule.every().hour.do(health_check)

    # 每周任务
    schedule.every().monday.at("10:00").do(weekly_summary)

    print("⏰ 定时任务已设置:")
    print("  - 每日 09:00: 每日报告")
    print("  - 每日 23:00: 同步到 ai_os")
    print("  - 每小时: 健康检查")
    print("  - 每周一 10:00: 周报摘要")


def run_scheduler():
    """运行调度器"""
    setup_schedule()

    print("\n🚀 调度器已启动，按 Ctrl+C 退出\n")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    run_scheduler()
