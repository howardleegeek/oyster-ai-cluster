---
task_id: B07-listmonk-deploy
project: marketing-stack
priority: 1
estimated_minutes: 20
depends_on: []
modifies: ["/opt/listmonk/docker-compose.yml", "/opt/listmonk/config.toml"]
executor: glm
---

## 目标
Deploy Listmonk email newsletter platform via Docker with postgres backend

## 约束
- Use official Listmonk Docker image: listmonk/listmonk:latest
- PostgreSQL 12+ for persistence
- Data volume: /opt/listmonk/data
- Port 9000 exposed
- Admin credentials: admin / (generate secure password)
- GCP node: codex-node-1 (load balance with n8n)
- Run as systemd service

## 验收标准
- [ ] docker-compose.yml created in /opt/listmonk/
- [ ] PostgreSQL container running with persistent volume
- [ ] Listmonk accessible on http://codex-node-1:9000
- [ ] docker-compose up -d succeeds
- [ ] Admin login works
- [ ] Database tables initialized: ./listmonk --install
- [ ] Service survives reboot (systemd enabled)
- [ ] Admin password saved to ~/.oyster-keys/listmonk/admin-password.txt

## 不要做
- 不要配置 SMTP (B08 handles)
- 不要创建 mailing lists
- 不要创建 email templates
- 不要导入 subscribers
