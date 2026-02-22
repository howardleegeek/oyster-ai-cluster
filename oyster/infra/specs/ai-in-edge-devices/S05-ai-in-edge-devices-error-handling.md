---
task_id: S05-ai-in-edge-devices-error-handling
project: ai-in-edge-devices
priority: 2
depends_on: ["S01-ai-in-edge-devices-bootstrap"]
modifies: ["backend/exceptions.py", "backend/middleware/error_handler.py"]
executor: glm
---
## 目标
实现统一的错误处理机制，确保API在异常情况下返回标准化的错误响应

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
