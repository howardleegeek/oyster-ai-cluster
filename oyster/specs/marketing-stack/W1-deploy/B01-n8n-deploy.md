---
task_id: B01-n8n-deploy
project: marketing-stack
priority: 1
estimated_minutes: 30
depends_on: []
modifies: ["/opt/n8n/docker-compose.yml", "/opt/n8n/.env"]
executor: glm
---

## 目标
Deploy n8n workflow automation via Docker on GCP codex-node-1 with postgres backend

## 约束
- Use official n8n Docker image (n8nio/n8n:latest)
- PostgreSQL 14+ for persistence
- Data volume: /opt/n8n/data
- Port 5678 exposed
- Environment: N8N_BASIC_AUTH_ACTIVE=true
- Run as systemd service for auto-restart
- GCP node: codex-node-1

## 验收标准
- [ ] docker-compose.yml created in /opt/n8n/
- [ ] PostgreSQL container running with persistent volume
- [ ] n8n accessible on http://codex-node-1:5678
- [ ] docker-compose up -d succeeds
- [ ] Service survives reboot (systemd enabled)
- [ ] Health check returns 200: curl http://localhost:5678/healthz

## 不要做
- 不要配置 SSL (B02 handles reverse proxy)
- 不要创建 workflows (后续 spec)
- 不要安装 custom nodes
- 不要修改其他 GCP 节点配置
