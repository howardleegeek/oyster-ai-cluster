---
task_id: B08-listmonk-config
project: marketing-stack
priority: 1
estimated_minutes: 20
depends_on: ["B07-listmonk-deploy"]
modifies: ["~/.oyster-keys/listmonk/lists.json", "/opt/listmonk/config.toml"]
executor: glm
---

## 目标
Configure Listmonk with Amazon SES SMTP, 6 mailing lists, and 4 email templates

## 约束
- SMTP provider: Amazon SES (use ~/.oyster-keys/aws/ses-credentials.json)
- Mailing lists: ClawMarketing, ClawPhones, WorldGlasses, GEM, getPuffy, OysterRepublic
- Email templates: newsletter (weekly), launch (product), engagement (re-engagement), welcome (onboarding)
- Each list: double opt-in enabled
- From address: noreply@oyster-labs.com
- Save list IDs to ~/.oyster-keys/listmonk/lists.json

## 验收标准
- [ ] SMTP configured in Settings → Messaging
- [ ] Test email sent successfully via SES
- [ ] 6 mailing lists created with unique IDs
- [ ] 4 email templates created in Templates section
- [ ] Lists saved to ~/.oyster-keys/listmonk/lists.json
- [ ] JSON format: {"list_name": {"id": 1, "uuid": "..."}}
- [ ] Double opt-in enabled for all lists

## 不要做
- 不要导入 subscribers (后续)
- 不要创建 campaigns
- 不要设置 bounce handling (后续)
- 不要修改 docker-compose
