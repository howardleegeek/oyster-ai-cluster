---
task_id: S02-ai驱动的p2p借贷平台-用户注册与认证
project: ai驱动的p2p借贷平台
priority: 1
depends_on: ["S01-ai驱动的p2p借贷平台-bootstrap"]
modifies: ["backend/auth.py", "backend/user.py", "tests/test_auth.py", "tests/test_user.py"]
executor: glm
---
## 目标
实现用户注册、登录和身份验证功能，包括密码加密和JWT token生成。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
