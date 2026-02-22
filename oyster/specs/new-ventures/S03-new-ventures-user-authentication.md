---
task_id: S03-new-ventures-user-authentication
project: new-ventures
priority: 1
depends_on: ["S01-new-ventures-bootstrap"]
modifies: ["backend/auth.py", "backend/routers/auth.py", "backend/schemas/user.py", "tests/test_auth.py"]
executor: glm
---
## 目标
实现用户注册和登录功能，包括密码哈希和JWT认证

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
