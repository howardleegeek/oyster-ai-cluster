---
task_id: B05-plausible-deploy
project: marketing-stack
priority: 1
estimated_minutes: 30
depends_on: []
modifies: ["/opt/plausible/docker-compose.yml", "/opt/plausible/plausible-conf.env"]
executor: glm
---

## 目标
Deploy Plausible Analytics via Docker on GCP with postgres and clickhouse backend

## 约束
- Use official Plausible hosting repo: https://github.com/plausible/hosting
- Services: plausible, postgres, clickhouse, smtp (optional)
- Data volumes: /opt/plausible/db-data, /opt/plausible/event-data
- Port 8100 exposed
- Environment: BASE_URL=http://glm-node-2:8100
- Generate SECRET_KEY_BASE (64 char random)
- GCP node: glm-node-2 (same as PostHog for resource sharing)
- Run as systemd service

## 验收标准
- [ ] docker-compose.yml created in /opt/plausible/
- [ ] postgres + clickhouse + plausible containers running
- [ ] Plausible UI accessible on http://glm-node-2:8100
- [ ] Database initialized successfully
- [ ] SECRET_KEY_BASE set in plausible-conf.env
- [ ] docker-compose ps shows all healthy
- [ ] Service survives reboot (systemd enabled)

## 不要做
- 不要注册 sites (B06 handles)
- 不要配置 SMTP (optional)
- 不要开放公网访问
- 不要修改 ClickHouse retention settings
