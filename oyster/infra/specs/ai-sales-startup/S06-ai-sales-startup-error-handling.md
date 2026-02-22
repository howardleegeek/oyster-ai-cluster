---
task_id: S06-ai-sales-startup-error-handling
project: ai-sales-startup
priority: 2
depends_on: ["S01-ai-sales-startup-bootstrap"]
modifies: ["backend/exceptions.py", "backend/main.py"]
executor: glm
---
## 目标
实现全局错误处理机制，确保API返回一致的错误响应

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
