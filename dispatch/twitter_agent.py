#!/usr/bin/env python3
"""
Twitter Integration - Agent 系统发推能力

功能:
- 发推文
- 回复
- 转发
- 获取时间线
- 搜索
- 互动 (点赞/转推/回复)
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# 配置
TWITTER_DIR = Path.home() / "Downloads" / "twitter-poster"


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [TwitterAgent] {msg}", flush=True)


class TwitterAgent:
    """Twitter 发推 Agent"""

    def __init__(self, worker_mode: str = "fast"):
        self.worker_mode = worker_mode  # "fast" or "slow"
        self.twitter_script = TWITTER_DIR / "twitter_poster.py"

    def post_tweet(self, content: str, media: List[str] = None) -> Dict:
        """发推文"""
        cmd = [
            "python3",
            str(self.twitter_script),
            "post",
            "--content",
            content,
        ]

        if media:
            cmd.extend(["--media"] + media)

        try:
            result = subprocess.run(
                cmd,
                cwd=str(TWITTER_DIR),
                capture_output=True,
                text=True,
                timeout=60,
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def reply(self, tweet_id: str, content: str) -> Dict:
        """回复推文"""
        cmd = [
            "python3",
            str(self.twitter_script),
            "reply",
            "--id",
            tweet_id,
            "--content",
            content,
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=str(TWITTER_DIR),
                capture_output=True,
                text=True,
                timeout=60,
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def retweet(self, tweet_id: str) -> Dict:
        """转发推文"""
        cmd = [
            "python3",
            str(self.twitter_script),
            "retweet",
            "--id",
            tweet_id,
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=str(TWITTER_DIR),
                capture_output=True,
                text=True,
                timeout=30,
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def like(self, tweet_id: str) -> Dict:
        """点赞"""
        cmd = [
            "python3",
            str(self.twitter_script),
            "like",
            "--id",
            tweet_id,
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=str(TWITTER_DIR),
                capture_output=True,
                text=True,
                timeout=30,
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_timeline(self, count: int = 20) -> List[Dict]:
        """获取时间线"""
        cmd = [
            "python3",
            str(self.twitter_script),
            "timeline",
            "--count",
            str(count),
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=str(TWITTER_DIR),
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except:
                    return [{"text": result.stdout}]
            return []
        except Exception as e:
            log(f"Error getting timeline: {e}")
            return []

    def search(self, query: str, count: int = 20) -> List[Dict]:
        """搜索推文"""
        cmd = [
            "python3",
            str(self.twitter_script),
            "search",
            "--query",
            query,
            "--count",
            str(count),
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=str(TWITTER_DIR),
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except:
                    return [{"text": result.stdout}]
            return []
        except Exception as e:
            log(f"Error searching: {e}")
            return []

    def engage(self, action: str = "like", count: int = 10) -> Dict:
        """批量互动 (点赞/转发/回复)"""
        cmd = [
            "python3",
            str(self.twitter_script),
            "engage",
            "--action",
            action,
            "--count",
            str(count),
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=str(TWITTER_DIR),
                capture_output=True,
                text=True,
                timeout=300,
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Twitter Agent")
    parser.add_argument(
        "action",
        choices=["post", "reply", "retweet", "like", "timeline", "search", "engage"],
    )
    parser.add_argument("--content", "-c")
    parser.add_argument("--id")
    parser.add_argument("--query", "-q")
    parser.add_argument("--count", "-n", type=int, default=10)
    parser.add_argument("--mode", default="fast")

    args = parser.parse_args()
    agent = TwitterAgent(args.mode)

    if args.action == "post":
        result = agent.post_tweet(args.content or "Test tweet")
        print(json.dumps(result, indent=2))
    elif args.action == "reply":
        result = agent.reply(args.id or "0", args.content or "Test reply")
        print(json.dumps(result, indent=2))
    elif args.action == "retweet":
        result = agent.retweet(args.id or "0")
        print(json.dumps(result, indent=2))
    elif args.action == "like":
        result = agent.like(args.id or "0")
        print(json.dumps(result, indent=2))
    elif args.action == "timeline":
        result = agent.get_timeline(args.count)
        print(json.dumps(result, indent=2))
    elif args.action == "search":
        result = agent.search(args.query or "AI", args.count)
        print(json.dumps(result, indent=2))
    elif args.action == "engage":
        result = agent.engage("like", args.count)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
