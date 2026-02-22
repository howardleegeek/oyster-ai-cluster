---
task_id: S03-deploy
project: clawmarketing
priority: 3
depends_on: [S02-verify-startup]
modifies: []
executor: codex-node-1
---

## 目标
部署 ClawMarketing 到生产环境

## 具体改动
1. 选择部署平台 (Render/Railway/AWS/Cloudflare 等)
2. 配置环境变量: DATABASE_URL, REDIS_URL, JWT_SECRET
3. 部署后端服务
4. curl 线上 endpoint 验证

## 验收标准
- [ ] 线上服务返回 {"status":"ok"}
