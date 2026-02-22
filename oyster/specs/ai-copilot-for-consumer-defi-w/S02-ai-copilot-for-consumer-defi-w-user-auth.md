---
task_id: S02-ai-copilot-for-consumer-defi-w-user-auth
project: ai-copilot-for-consumer-defi-w
priority: 1
depends_on: ["S01-ai-copilot-for-consumer-defi-w-bootstrap"]
modifies: ["backend/auth.py", "backend/main.py", "tests/test_auth.py"]
executor: glm
---
## 目标
实现用户身份验证功能，包括注册、登录和JWT令牌管理

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
