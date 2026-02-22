---
task_id: S06-ai-enhanced-neuromarketing-and-api-integration
project: ai-enhanced-neuromarketing-and
priority: 3
depends_on: ["S01-ai-enhanced-neuromarketing-and-bootstrap"]
modifies: ["backend/main.py", "tests/test_integration.py"]
executor: glm
---
## 目标
将所有模块集成到FastAPI中，并确保端到端的数据流

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
