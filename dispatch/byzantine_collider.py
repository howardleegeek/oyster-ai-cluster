#!/usr/bin/env python3
"""
拜占庭对撞器 (Byzantine Collider) - AI 增强版
多角度分析工具 - 将主题从不同维度进行"碰撞"，产生洞见

用法:
    python3 byzantine_collider.py <主题> [输出目录]
    python3 byzantine_collider.py <主题> --no-ai    # 纯框架模式
"""

import sys
import os
import json
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 默认输出目录
DEFAULT_OUTPUT_DIR = Path.home() / "ai_os/projects/Research/outputs/byzantine-collider"

# 分析维度
PERSPECTIVES = [
    {
        "name": "技术架构",
        "icon": "🏗️",
        "focus": "技术栈、架构设计、性能、扩展性、代码质量",
    },
    {"name": "产品体验", "icon": "🎯", "focus": "用户痛点、核心价值、UX/UI、留存转化"},
    {
        "name": "工程效率",
        "icon": "⚡",
        "focus": "开发流程、CI/CD、测试覆盖率、部署运维",
    },
    {
        "name": "商业模式",
        "icon": "💰",
        "focus": "成本结构、变现机会、竞争壁垒、增长引擎",
    },
    {"name": "风险安全", "icon": "🛡️", "focus": "安全漏洞、合规风险、依赖可靠性、灾备"},
    {
        "name": "未来趋势",
        "icon": "🔮",
        "focus": "技术趋势、市场机会、提前布局、颠覆风险",
    },
]


class LLMClient:
    """统一 LLM 客户端，支持 MiniMax 和 OpenAI"""

    def __init__(self):
        self.provider = None
        self.api_key = os.environ.get("MINIMAX_API_KEY")
        self.base_url = os.environ.get(
            "MINIMAX_BASE_URL", "https://api.minimax.io/v1/text/chatcompletion_v2"
        )
        self.model = os.environ.get("MINIMAX_MODEL", "MiniMax-M2.5")

        if self.api_key:
            self.provider = "minimax"
            return

        # 其次使用 OpenAI
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.environ.get("LLM_MODEL", "gpt-4o")

        if self.api_key:
            self.provider = "openai"

    async def chat(
        self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 2000
    ) -> str:
        if self.provider == "minimax":
            return await self._call_minimax(messages, temperature, max_tokens)
        elif self.provider == "openai":
            return await self._call_openai(messages, temperature, max_tokens)
        return "[无有效 API 配置]"

    async def _call_minimax(
        self, messages: List[Dict], temperature: float, max_tokens: int
    ) -> str:
        minimax_messages = [
            {"role": m.get("role", "user"), "content": m.get("content", "")}
            for m in messages
        ]

        payload = {
            "model": self.model,
            "messages": minimax_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    if resp.status != 200:
                        return f"[API 错误: {resp.status}]"
                    data = await resp.json()
                    return (
                        data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "[无内容]")
                    )
        except Exception as e:
            return f"[调用失败: {e}]"

    async def _call_openai(
        self, messages: List[Dict], temperature: float, max_tokens: int
    ) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    if resp.status != 200:
                        return f"[API 错误: {resp.status}]"
                    data = await resp.json()
                    return (
                        data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "[无内容]")
                    )
        except Exception as e:
            return f"[调用失败: {e}]"


def extract_lines(text: str, max_count: int = 5) -> List[str]:
    lines = []
    for line in text.split("\n"):
        line = line.strip()
        if line and len(line) > 5:
            line = line.lstrip("0123456789.>-) ")
            if line:
                lines.append(line)
                if len(lines) >= max_count:
                    break
    return lines


async def generate_collision(topic: str, use_ai: bool = True) -> Dict[str, Any]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    client = None
    if use_ai:
        client = LLMClient()
        if not client.api_key:
            print("⚠️ 未找到 API Key")
            client = None

    model_name = client.model if client else None
    analyses, summary, next_steps = [], "", []

    if client:
        print(f"🤖 AI 模式 ({client.provider}/{model_name})")

        # 只用 3 个核心维度
        core_perspectives = PERSPECTIVES[:3]

        # 构建 prompts
        prompts = []
        for p in core_perspectives:
            prompt = f"从{p['name']}角度分析「{topic}」。聚焦: {p['focus']}。给出3个洞见+2个建议。中文，150字内。"
            prompts.append(prompt)

        # 并行调用
        results = await asyncio.gather(
            *[
                client.chat([{"role": "user", "content": p}], max_tokens=600)
                for p in prompts
            ]
        )

        for i, text in enumerate(results):
            p = core_perspectives[i]
            analyses.append(
                {
                    "perspective": p["name"],
                    "icon": p["icon"],
                    "focus": p["focus"],
                    "insights": extract_lines(text),
                    "recommendations": extract_lines(text, 3),
                    "full_analysis": text,
                }
            )

        # 总结
        summary = await client.chat(
            [{"role": "user", "content": f"一句话总结「{topic}」的核心问题。30字内。"}],
            max_tokens=80,
        )
        next_steps_text = await client.chat(
            [{"role": "user", "content": f"「{topic}」的3个最重要行动。一行一个。"}],
            max_tokens=80,
        )
        next_steps = [l.strip() for l in next_steps_text.split("\n") if l.strip()]
    else:
        print("📝 框架模式")
        for p in PERSPECTIVES[:3]:
            analyses.append(
                {
                    "perspective": p["name"],
                    "icon": p["icon"],
                    "focus": p["focus"],
                    "insights": [],
                    "recommendations": [],
                    "full_analysis": None,
                }
            )

    return {
        "topic": topic,
        "timestamp": timestamp,
        "use_ai": client is not None,
        "provider": client.provider if client else None,
        "model": model_name,
        "perspectives": analyses,
        "summary": summary,
        "next_steps": next_steps,
    }


def save_collision(topic: str, data: Dict, output_dir: Optional[Path] = None) -> Path:
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_topic = "".join(c for c in topic if c.isalnum() or c in " -_").strip()[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_topic}_{timestamp}.md"
    filepath = output_dir / filename

    ai_badge = " 🤖" if data.get("use_ai") else ""
    model_info = (
        f" ({data.get('provider')}/{data.get('model')})" if data.get("provider") else ""
    )

    md = f"""# 拜占庭对撞{ai_badge}: {topic}
Generated: {datetime.now().isoformat()}{model_info}

---

## 综合分析

{data.get("summary", "(无)")}

---

"""
    for p in data["perspectives"]:
        md += f"\n### {p['icon']} {p['perspective']}\n\n**聚焦**: {p.get('focus', '')}\n\n"
        if p.get("insights"):
            md += "**洞见**:\n" + "\n".join(f"- {i}" for i in p["insights"]) + "\n"
        if p.get("recommendations"):
            md += (
                "\n**建议**:\n"
                + "\n".join(f"- {r}" for r in p["recommendations"])
                + "\n"
            )
        md += "\n---\n"

    md += "\n## 下一步行动\n\n"
    for i, step in enumerate(data.get("next_steps", []), 1):
        md += f"{i}. {step}\n"

    filepath.write_text(md, encoding="utf-8")
    json_path = filepath.with_suffix(".json")
    json_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return filepath


async def main_async():
    if len(sys.argv) < 2:
        print(__doc__)
        topic = input("请输入主题: ").strip()
        if not topic:
            sys.exit(1)
    else:
        topic = " ".join([a for a in sys.argv[1:] if a != "--no-ai"])

    use_ai = "--no-ai" not in sys.argv

    print(f"\n🎯 主题: {topic}")
    print("=" * 50)

    collision = await generate_collision(topic, use_ai=use_ai)
    output_path = save_collision(topic, collision)

    print(f"\n✅ 完成! 输出: {output_path}")

    if collision.get("summary"):
        print("\n" + "=" * 50)
        print("📊 综合分析:")
        print("-" * 50)
        print(collision["summary"][:500])


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
