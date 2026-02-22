---
task_id: S06-ai-in-ar-glasses-error-handling
project: ai-in-ar-glasses
priority: 2
depends_on: ["S01-ai-in-ar-glasses-bootstrap"]
modifies: ["backend/error_handling.py", "backend/logging.py"]
executor: glm
---
## 目标
实现健壮的错误处理和日志记录机制以支持系统稳定性

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
