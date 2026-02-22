---
task_id: S04-new-venture-ai-powered-decent-authentication-system
project: new-venture-ai-powered-decent
priority: 2
depends_on: ["S01-new-venture-ai-powered-decent-bootstrap"]
modifies: ["backend/router/auth.py", "backend/schemas/user.py", "backend/services/auth.py"]
executor: glm
---
## 目标
实现基本的用户认证系统，包括用户注册、登录和 JWT 令牌生成。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
