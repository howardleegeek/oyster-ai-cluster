---
task_id: S03-new-ventures-authentication
project: new-ventures
priority: 1
depends_on: ["S01-new-ventures-bootstrap"]
modifies: ["backend/auth.py", "backend/security.py", "tests/test_auth.py"]
executor: glm
---
## 目标
实现用户认证和授权机制（注册、登录、权限管理）

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
