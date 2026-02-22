---
task_id: D05-email-adapter
project: marketing-stack
priority: 2
estimated_minutes: 20
depends_on: [A01, B07]
modifies: ["oyster/social/email/adapter.py"]
executor: glm
---
## 目标
Create oyster/social/email/adapter.py implementing PlatformAdapter Protocol wrapping Listmonk REST API

## 约束
- Wrap Listmonk REST API endpoints
- post() sends campaign to list
- get_metrics() fetches open/click rates
- Use Listmonk API key from B07 setup
- Store credentials in ~/.oyster-keys/

## 验收标准
- [ ] adapter.py implements PlatformAdapter Protocol
- [ ] post() creates and sends campaigns via Listmonk
- [ ] get_metrics() returns campaign analytics
- [ ] API authentication works with stored key
- [ ] Error handling for failed sends
- [ ] pytest tests/social/email/test_adapter.py passes

## 不要做
- Don't build email template editor
- Don't add subscriber management yet
- Don't implement SMTP directly (use Listmonk)
