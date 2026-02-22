---
task_id: S06-ai-powered-on-device-llm-infer-testing
project: ai-powered-on-device-llm-infer
priority: 3
depends_on: ["S01-ai-powered-on-device-llm-infer-bootstrap"]
modifies: ["tests/test_inference.py", "tests/test_model_loading.py"]
executor: glm
---
## 目标
编写单元测试和集成测试以验证LLM推理功能

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
