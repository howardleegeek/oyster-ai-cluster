---
task_id: S03-ai-agent-for-on-device-ai-appl-implement-authentication
project: ai-agent-for-on-device-ai-appl
priority: 1
depends_on: ["S01-ai-agent-for-on-device-ai-appl-bootstrap"]
modifies: ["backend/auth.py", "backend/main.py", "backend/models/user.py", "tests/test_auth.py"]
executor: glm
---
## 目标
实现基本的用户认证机制（如JWT），确保API端点的安全性

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
