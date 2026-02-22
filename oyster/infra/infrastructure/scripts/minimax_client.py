#!/usr/bin/env python3
"""
MiniMax API 测试脚本
"""

import requests
import os

API_KEY = "sk-cp-T_Nj3VHn3G7Eyi3r50YumUyh-9cxvyV5xBd2RInrLvWKNHJsK-rCeMToiCy0rgWk2F1ZtOsZciTLjHxGYXipI2swY0ihhGfFY0K88q5XNJnLmBzqRbQLL_g"
BASE_URL = "https://api.minimax.io/v1/text/chatcompletion_v2"


def chat(message: str, model: str = "MiniMax-M2.5"):
    url = BASE_URL
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
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
        print(f"MiniMax: {result['choices'][0]['message']['content']}")
