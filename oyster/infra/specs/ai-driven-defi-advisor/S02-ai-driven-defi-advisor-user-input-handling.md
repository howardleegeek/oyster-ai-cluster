---
task_id: S02-ai-driven-defi-advisor-user-input-handling
project: ai-driven-defi-advisor
priority: 1
depends_on: ["S01-ai-driven-defi-advisor-bootstrap"]
modifies: ["backend/user_input.py"]
executor: glm
---
## 目标
实现用户输入处理模块，支持用户提交投资偏好和目标

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
