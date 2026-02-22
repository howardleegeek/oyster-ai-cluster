---
task_id: S02-ai-social-network-user-registration
project: ai-social-network
priority: 1
depends_on: ["S01-ai-social-network-bootstrap"]
modifies: ["backend/users.py", "backend/main.py", "tests/test_users.py"]
executor: glm
---
## 目标
实现用户注册功能，包括用户名、邮箱和密码的验证与存储

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
