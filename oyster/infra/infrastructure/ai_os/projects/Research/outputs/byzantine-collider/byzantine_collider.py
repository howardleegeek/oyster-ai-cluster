#!/usr/bin/env python3
"""
拜占庭对撞器 (Byzantine Collider) MVP
AI-to-AI 产品碰撞系统

Usage:
    python3 byzantine_collider.py --topic "拜占庭对撞器商业化"
    python3 byzantine_collider.py --topic "是否应该做小程序"
    python3 byzantine_collider.py --topic "AI 产品" --llm zhipu
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Optional

# LLM 适配层
try:
    from llm import create_llm, get_default_llm

    LLM_ADAPTER_AVAILABLE = True
except ImportError:
    LLM_ADAPTER_AVAILABLE = False
    print("⚠️ 警告: llm.py 未找到，使用默认实现")

# 默认实现（兼容）
try:
    from openai import OpenAI

    CLIENT = OpenAI()
except ImportError:
    CLIENT = None


# ============ Prompt 模板 ============

CHALLENGER_SYSTEM = """你是一位激进的产品批评家，专门找问题、挑毛病、质疑一切假设。

核心任务：
- 质疑"{topic}"的可行性
- 挑战任何假设
- 指出潜在风险和陷阱

提问风格：
- "但是如果...怎么办？"
- "这个假设真的成立吗？"
- "市场规模真的够大吗？"
- "用户真的会为此付费吗？"

约束：
- 只提问和质疑，不给解决方案
- 问题要具体、有挑战性
- 至少列出 5 个挑战点
- 用中文输出"""

DEFENDER_SYSTEM = """你是一位坚定的产品辩护者，为"{topic}"辩护。

核心任务：
- 为方案的商业化模式辩护
- 反驳挑战者的质疑
- 提供具体的证据和推理

回应风格：
- "这个挑战有道理，但我们可以..."
- "实际上，数据表明..."
- "竞争对手 XXX 已经验证了..."

约束：
- 必须回应每一个挑战
- 提供具体的数据、案例、或推理
- 不要轻易妥协
- 用中文输出"""


# ============ 核心函数 ============

# 全局 LLM 实例
_llm_instance = None


def get_llm(provider: str = None) -> Optional[object]:
    """获取 LLM 实例"""
    global _llm_instance

    if _llm_instance is not None:
        return _llm_instance

    if LLM_ADAPTER_AVAILABLE:
        _llm_instance = get_default_llm()
        return _llm_instance

    return None


def call_llm(
    system_prompt: str, user_prompt: str, model: str = None, provider: str = None
) -> str:
    """调用 LLM"""

    # 优先使用 LLM 适配器
    llm = get_llm(provider)
    if llm:
        return llm.chat(system_prompt, user_prompt)

    # 回退到默认实现
    if CLIENT is None:
        return "[模拟输出] 请配置 API key"

    response = CLIENT.chat.completions.create(
        model=model or "gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.8,
    )
    content = response.choices[0].message.content
    return content if content is not None else ""


def phase1_initialize(topic: str) -> dict:
    """阶段1：初始化 - 生成挑战者和辩护者立场"""
    print(f"\n📍 阶段1：初始化 - 主题: {topic}")

    # 挑战者生成挑战
    challenger_prompt = f"""请列出你对"{topic}"的所有质疑和挑战。"""
    challenger_output = call_llm(
        CHALLENGER_SYSTEM.format(topic=topic), challenger_prompt
    )

    # 辩护者生成回应
    defender_prompt = f"""挑战者提出了以下质疑，请为"{topic}"辩护：
    
{challenger_output}"""
    defender_output = call_llm(DEFENDER_SYSTEM.format(topic=topic), defender_prompt)

    return {
        "phase": 1,
        "topic": topic,
        "challenger": challenger_output,
        "defender": defender_output,
        "timestamp": datetime.now().isoformat(),
    }


def phase2_iterate(topic: str, previous: dict, round_num: int) -> dict:
    """阶段2：迭代碰撞"""
    print(f"\n🔄 阶段2：第 {round_num} 轮碰撞")

    # 挑战者攻击
    challenger_prompt = f"""主题：{topic}

上一轮辩护者的回应：
{previous.get("defender", "")}

请找出辩护者回应的逻辑漏洞、证据缺陷，并用反例攻击。"""
    challenger_output = call_llm(
        CHALLENGER_SYSTEM.format(topic=topic), challenger_prompt
    )

    # 辩护者防御
    defender_prompt = f"""主题：{topic}

挑战者的新一轮攻击：
{challenger_output}

请回应这些攻击，强化你的论点。"""
    defender_output = call_llm(DEFENDER_SYSTEM.format(topic=topic), defender_prompt)

    return {
        "phase": 2,
        "round": round_num,
        "challenger": challenger_output,
        "defender": defender_output,
        "timestamp": datetime.now().isoformat(),
    }


def phase3_converge(topic: str, history: list) -> dict:
    """阶段3：收敛判定 - 生成共识和分歧"""
    print(f"\n✅ 阶段3：收敛判定")

    # 汇总所有碰撞历史
    history_text = "\n\n".join(
        [
            f"第{round['round']}轮:\n挑战者: {round['challenger']}\n辩护者: {round['defender']}"
            for round in history
        ]
    )

    converge_prompt = f"""基于以下碰撞历史，请总结：

1. 共识点（双方同意的）
2. 分歧点（仍存在争议的）
3. 置信度评分（1-10）
4. 结论摘要

碰撞历史：
{history_text}"""

    # 用挑战者模板做总结（批判性视角）
    summary = call_llm(
        CHALLENGER_SYSTEM.format(topic=topic),  # 复用模板
        converge_prompt,
    )

    return {"phase": 3, "summary": summary, "timestamp": datetime.now().isoformat()}


def run_collision(
    topic: str, max_rounds: int = 3, output_file: Optional[str] = None
) -> dict:
    """运行完整的拜占庭对撞"""

    print(f"\n{'=' * 50}")
    print(f"🚀 拜占庭对撞器启动")
    print(f"📌 主题: {topic}")
    print(f"🔄 最大轮次: {max_rounds}")
    print(f"{'=' * 50}")

    # 阶段1：初始化
    result = phase1_initialize(topic)
    history = [result]

    # 阶段2：迭代碰撞
    for round_num in range(2, max_rounds + 1):
        result = phase2_iterate(topic, history[-1], round_num)
        history.append(result)
        print(f"   第 {round_num} 轮完成")

    # 阶段3：收敛
    convergence = phase3_converge(topic, history)

    # 完整结果
    full_result = {
        "topic": topic,
        "timestamp": datetime.now().isoformat(),
        "rounds": max_rounds,
        "history": history,
        "convergence": convergence,
    }

    # 保存结果
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(full_result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存: {output_file}")

    return full_result


# ============ 主入口 ============

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="拜占庭对撞器 MVP")
    parser.add_argument("--topic", "-t", required=True, help="碰撞主题")
    parser.add_argument("--rounds", "-r", type=int, default=3, help="碰撞轮次 (默认3)")
    parser.add_argument("--output", "-o", help="输出文件路径")

    args = parser.parse_args()

    if not CLIENT:
        print("⚠️ 警告: 未安装 openai 库，使用模拟输出")
        print("   安装: pip install openai")

    result = run_collision(args.topic, args.rounds, args.output)

    print(f"\n{'=' * 50}")
    print(f"🏁 对撞完成")
    print(f"{'=' * 50}")
