---
task_id: S125-linkedin-client
project: clawmarketing
priority: 2
depends_on: []
modifies: ["backend/clients/linkedin_client.py"]
executor: glm
---
## 目标
实现 LinkedIn API v2 客户端，支持发帖和获取 profile

## 约束
- 参考 backend/clients/twitter_client.py 架构
- OAuth 2.0 认证
- 速率限制遵循 LinkedIn API
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_linkedin_client.py 全绿
- [ ] LinkedInClient.post_message() 可发帖
- [ ] LinkedInClient.get_profile() 可获取用户信息
- [ ] 错误处理和重试逻辑完整

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
