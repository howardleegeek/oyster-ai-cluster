#!/usr/bin/env python3
"""
拜占庭对撞器 - LLM 适配层
支持多模型接入

支持:
- OpenAI (GPT-4o, GPT-4)
- Anthropic (Claude)
- 智谱 GLM (glm-4)
- 本地模型 (LocalAI)
"""

import os
import json
from typing import Optional
from abc import ABC, abstractmethod


# ============ LLM 接口定义 ============


class LLM(ABC):
    """LLM 基类"""

    @abstractmethod
    def chat(self, system: str, user: str, **kwargs) -> str:
        """返回文本响应"""
        pass


# ============ OpenAI 实现 ============


class OpenAILLM(LLM):
    def __init__(self, model: str = "gpt-4o", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def chat(self, system: str, user: str, **kwargs) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=kwargs.get("temperature", 0.8),
            max_tokens=kwargs.get("max_tokens", 4096),
        )

        content = response.choices[0].message.content
        return content if content else ""


# ============ Anthropic Claude 实现 ============


class AnthropicLLM(LLM):
    def __init__(
        self, model: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None
    ):
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

    def chat(self, system: str, user: str, **kwargs) -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)

        response = client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 4096),
            system=system,
            messages=[{"role": "user", "content": user}],
        )

        return response.content[0].text


# ============ 智谱 GLM 实现 ============


class ZhipuGLM(LLM):
    """智谱 GLM API"""

    def __init__(self, model: str = "glm-4", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY")
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"

    def chat(self, system: str, user: str, **kwargs) -> str:
        import requests

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": kwargs.get("temperature", 0.8),
            "max_tokens": kwargs.get("max_tokens", 4096),
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=kwargs.get("timeout", 120),
        )

        result = response.json()
        return result["choices"][0]["message"]["content"]


# ============ LocalAI 实现 ============


class LocalAILLM(LLM):
    """本地 LocalAI / Ollama"""

    def __init__(
        self, model: str = "llama3.2:1b", base_url: str = "http://localhost:8080"
    ):
        self.model = model
        self.base_url = base_url

    def chat(self, system: str, user: str, **kwargs) -> str:
        import requests

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": kwargs.get("temperature", 0.8),
        }

        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            timeout=kwargs.get("timeout", 300),
        )

        result = response.json()
        return result["choices"][0]["message"]["content"]


# ============ 工厂函数 ============


def create_llm(provider: str = "openai", **kwargs) -> LLM:
    """创建 LLM 实例"""

    providers = {
        "openai": OpenAILLM,
        "anthropic": AnthropicLLM,
        "claude": AnthropicLLM,  # alias
        "zhipu": ZhipuGLM,
        "glm": ZhipuGLM,  # alias
        "local": LocalAILLM,
        "localai": LocalAILLM,
    }

    if provider not in providers:
        raise ValueError(f"Unknown provider: {provider}")

    return providers[provider](**kwargs)


def get_default_llm() -> LLM:
    """获取默认 LLM（按优先级尝试）"""

    # 1. 优先用环境变量指定
    if os.getenv("BYZANTINE_LLM"):
        return create_llm(os.getenv("BYZANTINE_LLM"))

    # 2. 依次尝试可用
    if os.getenv("ZHIPU_API_KEY"):
        return create_llm("zhipu")
    if os.getenv("ANTHROPIC_API_KEY"):
        return create_llm("anthropic")
    if os.getenv("OPENAI_API_KEY"):
        return create_llm("openai")

    # 3. 默认 LocalAI
    return create_llm("local")


# ============ 使用示例 ============

if __name__ == "__main__":
    # 方式 1: 自动选择
    # llm = get_default_llm()

    # 方式 2: 指定模型
    llm = create_llm("zhipu", model="glm-4")

    # 测试
    response = llm.chat(
        system="你是一位有帮助的助手。", user="你好，请介绍一下你自己。"
    )
    print(response)
