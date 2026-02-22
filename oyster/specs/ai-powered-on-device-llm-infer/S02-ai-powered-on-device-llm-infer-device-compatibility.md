---
task_id: S02-ai-powered-on-device-llm-infer-device-compatibility
project: ai-powered-on-device-llm-infer
priority: 1
depends_on: ["S01-ai-powered-on-device-llm-infer-bootstrap"]
modifies: ["backend/main.py", "backend/config.py"]
executor: glm
---
## 目标
确保FastAPI后端与目标设备（如移动端或嵌入式设备）兼容

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
