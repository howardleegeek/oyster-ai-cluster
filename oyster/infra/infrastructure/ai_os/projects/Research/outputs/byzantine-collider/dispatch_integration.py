#!/usr/bin/env python3
"""
拜占庭对撞器 - Dispatch 集成

用法:
    # 直接运行
    python3 dispatch_integration.py --topic "AI 产品" --rounds 3

    # 或从 dispatch 调用
    # 在 spec 中添加:
    # executor: local
    # command: python3 path/to/dispatch_integration.py --topic "xxx"
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_via_llm(topic: str, rounds: int = 3) -> dict:
    """通过 LLM 运行碰撞（简化版）"""

    # 尝试导入
    try:
        from byzantine_collider import run_collision

        result = run_collision(topic, rounds)
        return result
    except ImportError as e:
        return {
            "error": f"导入失败: {e}",
            "topic": topic,
            "rounds": rounds,
            "timestamp": datetime.now().isoformat(),
        }


def run_via_api(
    topic: str, rounds: int = 3, api_url: str = "http://localhost:5000"
) -> dict:
    """通过 API 运行碰撞"""

    try:
        import requests

        response = requests.post(
            f"{api_url}/api/collision",
            json={"topic": topic, "rounds": rounds},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            collision_id = data.get("id")

            # 轮询等待结果
            print(f"碰撞 ID: {collision_id}, 等待结果...")

            for _ in range(60):  # 最多等 60 秒
                time.sleep(2)
                result_resp = requests.get(f"{api_url}/api/collision/{collision_id}")
                if result_resp.status_code == 200:
                    result_data = result_resp.json()
                    if result_data.get("status") == "completed":
                        return result_data
                    elif result_data.get("status") == "failed":
                        return result_data

            return {"error": "超时", "collision_id": collision_id}
        else:
            return {"error": f"API 错误: {response.status_code}"}

    except Exception as e:
        return {"error": str(e)}


def dispatch_main():
    """Dispatch 入口"""

    parser = argparse.ArgumentParser(description="拜占庭对撞器 - Dispatch 集成")
    parser.add_argument("--topic", "-t", required=True, help="碰撞主题")
    parser.add_argument("--rounds", "-r", type=int, default=3, help="碰撞轮次")
    parser.add_argument(
        "--mode", "-m", choices=["llm", "api"], default="api", help="运行模式"
    )
    parser.add_argument("--api-url", default="http://localhost:5000", help="API 地址")
    parser.add_argument("--output", "-o", help="输出文件")

    args = parser.parse_args()

    print(f"""
⚔️  拜占庭对撞器
   主题: {args.topic}
   轮次: {args.rounds}
   模式: {args.mode}
""")

    # 运行碰撞
    if args.mode == "api":
        result = run_via_api(args.topic, args.rounds, args.api_url)
    else:
        result = run_via_llm(args.topic, args.rounds)

    # 输出结果
    output = {
        "topic": args.topic,
        "rounds": args.rounds,
        "timestamp": datetime.now().isoformat(),
        "result": result,
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存: {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))

    # 返回状态码
    if result.get("error"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(dispatch_main())
