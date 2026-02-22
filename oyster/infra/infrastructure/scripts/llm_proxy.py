#!/usr/bin/env python3
"""
简单 LLM API 代理 - 支持 MiniMax
"""

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# MiniMax 配置
MINIMAX_API_KEY = "sk-cp-T_Nj3VHn3G7Eyi3r50YumUyh-9cxvyV5xBd2RInrLvWKNHJsK-rCeMToiCy0rgWk2F1ZtOsZciTLjHxGYXipI2swY0ihhGfFY0K88q5XNJnLmBzqRbQLL_g"
MINIMAX_BASE_URL = "https://api.minimax.io/v1/text/chatcompletion_v2"


@app.route("/v1/chat/completions", methods=["POST"])
def chat():
    data = request.json
    model = data.get("model", "MiniMax-M2.5")

    # 转发到 MiniMax
    url = MINIMAX_BASE_URL
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, json=data)
    return jsonify(response.json())


@app.route("/v1/models", methods=["GET"])
def models():
    return jsonify(
        {"data": [{"id": "MiniMax-M2.5", "object": "model", "owned_by": "MiniMax"}]}
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4001)
