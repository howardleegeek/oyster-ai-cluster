---
task_id: S05-deploy-backend-gcp
project: clawmarketing
priority: 5
depends_on: [S02-verify-startup]
modifies: []
executor: codex-node-1
---

## 目标
部署 ClawMarketing 后端到 GCP 服务器，暴露公网访问

## 具体改动
1. 安装依赖: pip3 install --break-system-packages python-jose[cryptography] passlib bcrypt python-multipart httpx sqlalchemy pydantic pydantic-settings aiosqlite
2. 启动后端在 0.0.0.0:80 或 8000
3. 配置 Nginx 反向代理到 8000 端口
4. 或者直接用 uvicorn --host 0.0.0.0 --port 80
5. 验证: curl http://<公网IP>/

## 验收标准
- [ ] curl http://<公网IP>/ 返回 {"status":"ok"}
- [ ] 前端可以调用后端 API
