---
task_id: S03-ai-social-network-user-authentication
project: ai-social-network
priority: 1
depends_on: ["S01-ai-social-network-bootstrap"]
modifies: ["backend/auth.py", "backend/main.py", "tests/test_auth.py"]
executor: glm
---
## 目标
实现用户登录和认证功能，使用JWT生成和验证用户令牌

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
