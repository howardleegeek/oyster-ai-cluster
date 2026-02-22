---
task_id: B11-serpbear-deploy
project: marketing-stack
priority: 1
estimated_minutes: 20
depends_on: []
modifies: ["/opt/serpbear/docker-compose.yml", "/opt/serpbear/.env"]
executor: glm
---

## 目标
Deploy SerpBear SEO rank tracking via Docker with built-in SQLite database

## 约束
- Use official SerpBear image: towfiqi/serpbear:latest
- Database: SQLite (built-in, no postgres needed)
- Data volume: /opt/serpbear/data
- Port 3001 exposed
- Environment: SECRET (generate 32 char), USER=admin, PASSWORD=(generate)
- GCP node: codex-node-1 (group with n8n/listmonk)
- Run as systemd service

## 验收标准
- [ ] docker-compose.yml created in /opt/serpbear/
- [ ] SerpBear container running
- [ ] SerpBear UI accessible on http://codex-node-1:3001
- [ ] docker-compose up -d succeeds
- [ ] Admin login works
- [ ] SQLite database created in /opt/serpbear/data
- [ ] Service survives reboot (systemd enabled)
- [ ] Credentials saved to ~/.oyster-keys/serpbear/admin-creds.txt

## 不要做
- 不要添加 domains (B12 handles)
- 不要添加 keywords
- 不要配置 Google Search Console
- 不要设置 email alerts
