---
task_id: S029-linkedin-adapter
project: marketing-stack
priority: 2
estimated_minutes: 30
depends_on: [A01]
modifies: ["oyster/social/linkedin/adapter.py"]
executor: glm
---
## 目标
Create oyster/social/linkedin/adapter.py implementing PlatformAdapter Protocol using LinkedIn API v2 with OAuth2 + REST

## 约束
- Use LinkedIn API v2 (OAuth2 + REST endpoints)
- Implement post() and get_metrics() methods
- Reply not supported initially (LinkedIn limitation)
- Store OAuth tokens in ~/.oyster-keys/
- Handle API rate limits and errors

## 验收标准
- [ ] adapter.py implements PlatformAdapter Protocol
- [ ] post() creates UGC posts via LinkedIn API
- [ ] get_metrics() fetches engagement stats
- [ ] OAuth2 authentication flow works
- [ ] Tokens stored securely in ~/.oyster-keys/
- [ ] pytest tests/social/linkedin/test_adapter.py passes

## 不要做
- Don't implement reply() (not supported by LinkedIn)
- Don't store tokens in code or .env
- Don't add UI for OAuth flow yet
