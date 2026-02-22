---
task_id: B02-n8n-config
project: marketing-stack
priority: 1
estimated_minutes: 20
depends_on: ["B01-n8n-deploy"]
modifies: ["/opt/caddy/Caddyfile", "~/.oyster-keys/n8n/credentials.json"]
executor: glm
---

## 目标
Configure n8n with SSL reverse proxy, admin account, and credential vault for marketing integrations

## 约束
- Caddy reverse proxy for SSL (auto cert)
- Domain: n8n.oyster-labs.internal (或使用实际域名)
- Admin user: admin@oyster-labs.com
- API key generation for automation access
- Credential types: Twitter API v2, Bluesky API, SMTP (Amazon SES), PostHog, Plausible
- Save API key to ~/.oyster-keys/n8n/api-key.txt

## 验收标准
- [ ] Caddy reverse proxy running, SSL cert obtained
- [ ] n8n accessible via HTTPS
- [ ] Admin account created and tested login
- [ ] API key generated and saved to ~/.oyster-keys/n8n/
- [ ] 5 credential templates created in n8n vault
- [ ] curl test with API key succeeds: curl -H "X-N8N-API-KEY: xxx" https://n8n.../api/v1/workflows

## 不要做
- 不要填充实际 API credentials (后续手动)
- 不要创建 workflows
- 不要开放公网访问 (内网 only)
- 不要修改 n8n docker-compose (B01 handles)
