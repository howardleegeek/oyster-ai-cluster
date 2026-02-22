---
task_id: S02-ai-sales-startup-user-authentication
project: ai-sales-startup
priority: 1
depends_on: ["S01-ai-sales-startup-bootstrap"]
modifies: ["backend/authentication.py", "backend/main.py"]
executor: glm
---
## 目标
实现用户认证功能，包括注册、登录和JWT令牌生成

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
