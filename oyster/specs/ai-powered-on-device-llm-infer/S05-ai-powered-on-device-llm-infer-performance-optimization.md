---
task_id: S05-ai-powered-on-device-llm-infer-performance-optimization
project: ai-powered-on-device-llm-infer
priority: 2
depends_on: ["S01-ai-powered-on-device-llm-infer-bootstrap"]
modifies: ["backend/inference.py", "backend/utils.py"]
executor: glm
---
## 目标
优化LLM推理的性能，包括延迟和内存使用

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
