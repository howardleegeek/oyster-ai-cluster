#!/usr/bin/env python3
"""
Spec 碰撞系统 - 用算力换无 Bug

核心思路：
- Spec = hypothesis = 解法空间中的一个点
- 测试 = fitness function
- 碰撞 = 在解空间中搜索，直到找到能通过所有测试的解

输入: 任务目标 + 测试用例
迭代:
  1. 生成 N 个 spec 变体
  2. 并行调度到集群
  3. 跑测试
  4. 选最优
  5. 进化（成功→突变，失败→重启）
输出: 100% 测试通过的代码
"""

import sys
import os
import json
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# 配置
MAX_GENERATIONS = 10  # 最大迭代次数
VARIANTS_PER_GEN = 5  # 每代变体数
MIN_SUCCESS_RATE = 0.8  # 最小成功率阈值


def call_minimax(prompt: str, system_prompt: str = None) -> str:
    """调用 MiniMax API"""
    import urllib.request
    import urllib.error

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
            "temperature": 0.7,
        }
    ).encode()

    req = urllib.request.Request(
        "https://api.minimax.io/v1/text/chatcompletion_v2",
        data=data,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API Error: {e}")
        return ""


def generate_spec_variants(
    task: str, project: str, n: int = 5, context: str = None, success_spec: str = None
) -> List[str]:
    """生成 N 个 spec 变体

    Args:
        task: 任务目标
        project: 项目名
        n: 变体数量
        context: 上一轮上下文（可选）
        success_spec: 上一轮成功的 spec（用于进化）
    """

    system_prompt = """你是一个 AI 代码工厂的 spec 生成器，专门生成"能通过测试"的 hypothesis。

核心思路：
- Spec = hypothesis = 解法路径
- 测试通过 = hypothesis 正确
- 目标是生成"能解决问题"的 spec，不是"看起来对"的 spec

要求：
1. 每个 spec 必须有不同的"解法路径"
2. 每个 spec 必须是完整的、可执行的
3. 用 YAML front-matter + Markdown 格式
4. 验收标准必须可测试

输出格式：直接输出 N 个 spec，用 "---SPEC_SEPARATOR---" 分隔"""

    # 构建 prompt
    context_section = ""
    if success_spec:
        context_section = f"""
上一轮成功的 spec（这是对的思路，参考它来生成更好的）：
---
{success_spec}
---
"""
    elif context:
        context_section = f"""
上一轮尝试过的方案：
{context}
"""

    prompt = f"""生成 {n} 个不同的 spec 变体来解决这个任务。

任务目标: {task}
项目: {project}
{context_section}
重要：
1. 每个 spec 必须有不同的技术路径/架构选择
2. 验收标准必须可测试
3. 约束要清晰
4. 尝试不同的思路，不要总用同一种方法

开始生成："""

    result = call_minimax(prompt, system_prompt)

    # 解析结果
    if not result:
        return []

    specs = result.split("---SPEC_SEPARATOR---")
    return [s.strip() for s in specs if s.strip()]


def run_dispatch(project: str, spec_path: str) -> Dict:
    """运行 dispatch 执行 spec，返回结果"""

    # 调用 dispatch
    cmd = f"python3 ~/Downloads/dispatch/dispatch.py start {project}"

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=60
        )
        return {"status": "started", "output": result.stdout}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def check_tests(project: str) -> Tuple[int, int]:
    """检查测试通过率

    Returns:
        (passed, total) 测试通过数/总数
    """
    # TODO: 集成到 dispatch 报告系统
    # 这里简化，实际需要读取测试结果
    return (0, 0)


def evolve(success_specs: List[str], failed_specs: List[str]) -> str:
    """进化 - 基于成功/失败的经验生成新的 prompt"""

    context = []

    if success_specs:
        context.append(f"成功的思路（可以继续改进）:\n{success_specs[0][:500]}")

    if failed_specs:
        context.append(f"失败的思路（避免再试）:\n{failed_specs[0][:500]}")

    return "\n\n".join(context)


def collision_loop(task: str, project: str, test_cmd: str = None) -> Dict:
    """碰撞主循环

    迭代生成 spec → 执行 → 测试 → 进化，直到找到解

    Returns:
        最终结果
    """

    print(f"\n{'=' * 60}")
    print(f"🎯 开始碰撞: {task}")
    print(f"📁 项目: {project}")
    print(f"{'=' * 60}\n")

    best_spec = None
    context = ""
    all_generations = []

    for generation in range(MAX_GENERATIONS):
        print(f"\n📌 第 {generation + 1}/{MAX_GENERATIONS} 代")

        # 1. 生成变体
        print(f"  🔄 生成 {VARIANTS_PER_GEN} 个 spec 变体...")

        success_spec = best_spec if best_spec else None
        specs = generate_spec_variants(
            task, project, VARIANTS_PER_GEN, context, success_spec
        )

        if not specs:
            print("  ⚠️ 生成失败，重新尝试...")
            time.sleep(5)
            continue

        print(f"  ✅ 生成了 {len(specs)} 个变体")

        # 2. 保存 spec
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        spec_dir = Path(
            f"~/Downloads/specs/{project}/collision-{timestamp}"
        ).expanduser()
        spec_dir.mkdir(parents=True, exist_ok=True)

        spec_paths = []
        for i, spec in enumerate(specs, 1):
            path = spec_dir / f"gen{generation + 1:02d}_v{i:02d}.md"
            path.write_text(spec)
            spec_paths.append((path, spec))
            print(f"    📄 {path.name}")

        # 3. 调度执行（这里简化，实际需要调用 dispatch）
        print(f"  🚀 调度到集群...")

        # 4. 模拟结果（实际需要真实执行+测试）
        # 这里先模拟，实际需要:
        # - 运行 dispatch
        # - 收集测试结果
        # - 判定是否通过

        print(f"  ⏳ 等待执行结果...")

        # 模拟评估 - 实际这里需要读取测试结果
        # success_count = sum(1 for p, s in spec_paths if run_tests(p))

        # 记录这一代
        all_generations.append(
            {"generation": generation + 1, "specs": spec_paths, "best": best_spec}
        )

        # 进化上下文
        context = evolve([best_spec] if best_spec else [], [])

        # 检查是否全部失败
        if generation > 2:
            print(f"  ⚠️ 尝试多次未成功，考虑重启思路...")
            context = ""
            best_spec = None

    # 汇总结果
    return {
        "task": task,
        "project": project,
        "generations": len(all_generations),
        "best_spec": best_spec,
        "status": "completed" if best_spec else "failed",
    }


def main():
    parser = argparse.ArgumentParser(description="Spec 碰撞系统 - 用算力换无 Bug")
    parser.add_argument("task", help="任务目标（一句话）")
    parser.add_argument("-p", "--project", required=True, help="项目名")
    parser.add_argument(
        "-n", "--max-generations", type=int, default=10, help="最大迭代次数"
    )
    parser.add_argument("-v", "--variants", type=int, default=5, help="每代变体数")
    parser.add_argument("-t", "--test", help="测试命令")

    args = parser.parse_args()

    global MAX_GENERATIONS, VARIANTS_PER_GEN
    MAX_GENERATIONS = args.max_generations
    VARIANTS_PER_GEN = args.variants

    # 开始碰撞
    result = collision_loop(args.task, args.project, args.test)

    print(f"\n{'=' * 60}")
    print(f"🏁 碰撞完成")
    print(f"状态: {result['status']}")
    print(f"代数: {result['generations']}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
