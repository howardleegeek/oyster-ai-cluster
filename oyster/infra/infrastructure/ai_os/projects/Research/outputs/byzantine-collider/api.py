#!/usr/bin/env python3
"""
拜占庭对撞器 - API 服务
基于 Flask 的 REST API + Webhook 支持

启动:
    python3 api.py
    # 默认端口 5000

接口:
    POST /api/collision     - 发起碰撞
    GET  /api/collision/:id - 获取结果
    POST /api/research     - 网络调研
    POST /webhook/collision - Webhook 回调
    GET  /                - Web UI
    GET  /health          - 健康检查
"""

import os
import uuid
import threading
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS

app = Flask(__name__, static_folder="web", static_url_path="")
CORS(app)

# 存储结果（生产环境用 Redis）
results = {}
webhooks = {}


# Webhook 回调
def call_webhook(webhook_url, payload):
    """异步调用 Webhook"""
    try:
        import requests

        threading.Thread(
            target=lambda: requests.post(webhook_url, json=payload, timeout=10)
        ).start()
    except Exception as e:
        print(f"Webhook 调用失败: {e}")


# ============ API 端点 ============


@app.route("/", methods=["GET"])
def index():
    """Web UI"""
    return send_from_directory("web", "index.html")


@app.route("/health", methods=["GET"])
def health():
    """健康检查"""
    return jsonify(
        {"status": "ok", "timestamp": datetime.now().isoformat(), "version": "1.2"}
    )


@app.route("/api/collision", methods=["POST"])
def create_collision():
    """发起碰撞"""
    data = request.json or {}

    topic = data.get("topic")
    rounds = data.get("rounds", 3)
    template = data.get("template", "default")
    llm = data.get("llm", "zhipu")
    webhook_url = data.get("webhook")

    if not topic:
        return jsonify({"error": "topic is required"}), 400

    # 生成 ID
    collision_id = str(uuid.uuid4())[:8]

    # 保存请求信息
    results[collision_id] = {
        "id": collision_id,
        "topic": topic,
        "rounds": rounds,
        "template": template,
        "llm": llm,
        "status": "running",
        "created_at": datetime.now().isoformat(),
    }

    # 异步处理
    def run_and_notify():
        try:
            # 尝试导入并运行
            from byzantine_collider import run_collision

            result = run_collision(topic, rounds)

            results[collision_id].update(
                {
                    "result": result,
                    "status": "completed",
                    "completed_at": datetime.now().isoformat(),
                }
            )
        except Exception as e:
            results[collision_id].update(
                {
                    "status": "failed",
                    "error": str(e),
                }
            )

        # Webhook 回调
        if webhook_url:
            call_webhook(webhook_url, results[collision_id])

    # 启动后台任务
    threading.Thread(target=run_and_notify).start()

    return jsonify(
        {
            "id": collision_id,
            "status": "running",
            "message": "碰撞已开始，请使用 ID 查询结果",
        }
    )


@app.route("/api/collision/<collision_id>", methods=["GET"])
def get_collision(collision_id):
    """获取碰撞结果"""
    if collision_id not in results:
        return jsonify({"error": "not found"}), 404

    return jsonify(results[collision_id])


@app.route("/api/collision/<collision_id>", methods=["DELETE"])
def delete_collision(collision_id):
    """删除碰撞记录"""
    if collision_id not in results:
        return jsonify({"error": "not found"}), 404

    del results[collision_id]
    return jsonify({"status": "deleted"})


@app.route("/api/research", methods=["POST"])
def create_research():
    """网络调研"""
    data = request.json or {}

    query = data.get("query")
    if not query:
        return jsonify({"error": "query is required"}), 400

    try:
        from research import NetworkResearcher

        researcher = NetworkResearcher()
        report = researcher.research(query)

        return jsonify(
            {"query": query, "report": report, "timestamp": datetime.now().isoformat()}
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ Webhook 端点 ============


@app.route("/api/webhook", methods=["POST"])
def register_webhook():
    """注册 Webhook（简化版：存储在内存）"""
    data = request.json or {}
    webhook_url = data.get("url")

    if not webhook_url:
        return jsonify({"error": "url is required"}), 400

    webhook_id = str(uuid.uuid4())[:8]
    webhooks[webhook_id] = {
        "url": webhook_url,
        "created_at": datetime.now().isoformat(),
    }

    return jsonify({"webhook_id": webhook_id, "status": "registered"})


@app.route("/api/webhook/<webhook_id>", methods=["DELETE"])
def unregister_webhook(webhook_id):
    """注销 Webhook"""
    if webhook_id not in webhooks:
        return jsonify({"error": "not found"}), 404

    del webhooks[webhook_id]
    return jsonify({"status": "deleted"})


# ============ 主入口 ============

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="拜占庭对撞器 API")
    parser.add_argument("--port", "-p", type=int, default=5000, help="端口")
    parser.add_argument("--debug", "-d", action="store_true", help="调试模式")

    args = parser.parse_args()

    # 确保 web 目录存在
    web_dir = os.path.join(os.path.dirname(__file__), "web")
    if os.path.exists(web_dir):
        app.static_folder = web_dir

    print(f"""
⚔️  拜占庭对撞器 API v1.2
   http://localhost:{args.port}

可用接口:
   POST /api/collision       - 发起碰撞
   GET  /api/collision/:id   - 获取结果
   DELETE /api/collision/:id - 删除记录
   POST /api/research       - 网络调研
   POST /api/webhook       - 注册 Webhook
   GET  /                   - Web UI
   GET  /health            - 健康检查

Webhook 示例:
   curl -X POST http://localhost:{args.port}/api/collision \\
     -H "Content-Type: application/json" \\
     -d '{{"topic": "AI 产品", "webhook": "https://your-server.com/callback"}}'
""")

    app.run(host="0.0.0.0", port=args.port, debug=args.debug)
