---
task_id: S017-twenty-deploy
project: marketing-stack
priority: 1
estimated_minutes: 30
depends_on: []
modifies: ["/opt/twenty/docker-compose.yml", "/opt/twenty/.env"]
executor: glm
---

## 目标
Deploy Twenty CRM via Docker on GCP with postgres backend and Redis cache

## 约束
- Use official Twenty docker-compose: https://github.com/twentyhq/twenty
- Services: twenty-server, twenty-worker, postgres, redis
- Data volumes: /opt/twenty/postgres-data
- Port 3000 exposed
- Environment: POSTGRES_PASSWORD (generate), JWT_SECRET (generate)
- GCP node: glm-node-2 (group CRM + analytics)
- Run as systemd service
- Node version: 18+

## 验收标准
- [ ] docker-compose.yml created in /opt/twenty/
- [ ] postgres + redis + twenty-server + twenty-worker running
- [ ] Twenty UI accessible on http://glm-node-2:3000
- [ ] Database migrations completed
- [ ] docker-compose ps shows all services healthy
- [ ] Service survives reboot (systemd enabled)
- [ ] Secrets saved to ~/.oyster-keys/twenty/secrets.env

## 不要做
- 不要创建 workspaces (B10 handles)
- 不要配置 custom fields
- 不要导入 contacts
- 不要配置 email sync
