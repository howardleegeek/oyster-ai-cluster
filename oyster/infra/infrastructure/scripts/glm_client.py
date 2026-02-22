#!/usr/bin/env python3
"""
GLM API 简单调用脚本
"""

import requests
import os

GLM_API_KEY = "6feb6223d2d645f98f0b2f28932431e2.rK1z3jOTh0a38pic"
GLM_BASE_URL = "https://api.z.ai/api/paas/v4"


def chat(message: str, model: str = "glm-4.5"):
    """发送聊天请求"""
    url = f"{GLM_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {GLM_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {"model": model, "messages": [{"role": "user", "content": message}]}

    response = requests.post(url, headers=headers, json=data)
    return response.json()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        msg = " ".join(sys.argv[1:])
    else:
        msg = "Hello"

    print(f"User: {msg}")
    result = chat(msg)
    print(f"Response: {result}")
    if "choices" in result:
        print(f"GLM: {result['choices'][0]['message']['content']}")
