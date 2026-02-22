---
task_id: S05-new-ventures-error-handling
project: new-ventures
priority: 2
depends_on: ["S01-new-ventures-bootstrap"]
modifies: ["backend/errors.py", "backend/middleware/error_handler.py", "backend/main.py"]
executor: glm
---
## 目标
实现统一的错误处理机制，包括自定义异常和错误响应格式

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
