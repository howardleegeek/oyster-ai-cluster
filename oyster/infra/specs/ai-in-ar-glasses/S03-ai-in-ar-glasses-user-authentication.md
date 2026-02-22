---
task_id: S03-ai-in-ar-glasses-user-authentication
project: ai-in-ar-glasses
priority: 2
depends_on: ["S01-ai-in-ar-glasses-bootstrap"]
modifies: ["backend/authentication.py", "backend/user.py"]
executor: glm
---
## 目标
开发用户认证和授权系统以支持个性化AI功能

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
