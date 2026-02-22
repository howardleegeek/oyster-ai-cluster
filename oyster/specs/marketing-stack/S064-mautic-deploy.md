---
task_id: S064-mautic-deploy
project: marketing-stack
priority: 3
estimated_minutes: 30
depends_on: []
modifies: ["oyster/infra/docker-compose-marketing.yml", "oyster/infra/mautic-config/"]
executor: glm
---
## 目标
Deploy Mautic marketing automation via Docker on port 8080 with persistent storage at /opt/mautic

## 约束
- Use official Mautic Docker image
- MySQL/MariaDB backend
- Persist volumes: /opt/mautic/data, /opt/mautic/config
- Internal network only, reverse proxy for external access
- API keys in ~/.oyster-keys/

## 验收标准
- [ ] Mautic accessible at http://localhost:8080
- [ ] Database initialized and persistent
- [ ] docker-compose up -d starts successfully
- [ ] Mautic admin panel accessible
- [ ] Configuration survives container restart

## 不要做
- No public port exposure without reverse proxy
- No hardcoded credentials in docker-compose
- No UI changes to Mautic itself
