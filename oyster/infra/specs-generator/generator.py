#!/usr/bin/env python3
"""
Spec 变体生成器 - 在"假设空间"里做算力碰撞

输入: 任务目标 (一句话)
输出: N 个不同方向的 spec (hypothesis)

本质: 用算力换正确性，不靠人写代码
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path


# MiniMax API
def call_minimax(prompt: str, system_prompt: str = None) -> str:
    """调用 MiniMax API"""
    key_file = os.path.expanduser("~/.oyster-keys/minimax.env")
    API_KEY = os.environ.get("MINIMAX_API_KEY")
    if not API_KEY and os.path.exists(key_file):
        for line in open(key_file):
            if line.startswith("export MINIMAX_API_KEY="):
                API_KEY = line.split("=", 1)[1].strip().strip('"')
                break

    if not API_KEY:
        raise Exception("MINIMAX_API_KEY not found")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    data = json.dumps(
        {
            "model": "MiniMax-M2.5",
            "messages": messages,
            "max_tokens": 16384,
            "temperature": 0.7,  # 高温度，多样性
        }
    ).encode()

    import urllib.request

    req = urllib.request.Request(
        "https://api.minimax.io/v1/text/chatcompletion_v2",
        data=data,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
    )

    import urllib.request

    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
        return result["choices"][0]["message"]["content"]


def generate_spec_variants(task: str, project: str, n: int = 5) -> list:
    """生成 N 个不同方向的 spec"""

    system_prompt = """你是一个 AI 代码工厂的 spec 生成器。你的任务是从一个任务目标生成多个不同的"假设"（spec）。

核心思路：
- Spec = hypothesis = 解法路径
- 好的 spec = 一个有希望的解法方向
- 不同的 spec = 不同的解法思路

要求：
1. 每个 spec 必须有不同的"解法路径"
2. 每个 spec 必须是完整的、可执行的
3. 用 YAML front-matter + Markdown 格式
4. 每个 spec 的 task_id 格式: S01-xxx-v{1,2,3...}

输出格式：直接输出 N 个 spec，用 "---SPEC_SEPARATOR---" 分隔"""

    prompt = f"""生成 {n} 个不同的 spec。每个 spec 要有不同的解法方向。

任务目标: {task}
项目: {project}

注意：
1. 每个 spec 必须有不同的技术路径/架构选择
2. 约束要清晰
3. 验收标准要可测试

开始生成："""

    prompt = f"生成 {n} 个不同的 spec。每个 spec 要有不同的解法方向。\n\n任务目标: {task}\n项目: {project}"

    result = call_minimax(prompt, system_prompt)

    # 解析结果
    specs = result.split("---SPEC_SEPARATOR---")

    return [s.strip() for s in specs if s.strip()]


def main():
    parser = argparse.ArgumentParser(description="Spec 变体生成器")
    parser.add_argument("task", help="任务目标（一句话）")
    parser.add_argument("-p", "--project", required=True, help="项目名")
    parser.add_argument("-n", "--variants", type=int, default=5, help="变体数量")
    parser.add_argument("-o", "--output", help="输出目录")

    args = parser.parse_args()

    print(f"🎯 生成 {args.variants} 个 spec 变体...")
    print(f"📋 任务: {args.task}")
    print(f"📁 项目: {args.project}")
    print()

    specs = generate_spec_variants(args.task, args.project, args.variants)

    # 保存
    output_dir = args.output or f"~/Downloads/specs/{args.project}"
    output_dir = os.path.expanduser(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for i, spec in enumerate(specs, 1):
        filename = f"{output_dir}/S01-variant-{i:02d}_{timestamp}.md"
        with open(filename, "w") as f:
            f.write(spec)
        print(f"✅ 生成: {filename}")

    print(f"\n✨ 完成！生成了 {len(specs)} 个 spec 变体")
    print("这些变体代表不同的解法路径，算力会碰撞出最优解。")


if __name__ == "__main__":
    main()
