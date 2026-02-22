---
task_id: S04-ai-powered-on-device-llm-infer-model-loading
project: ai-powered-on-device-llm-infer
priority: 1
depends_on: ["S01-ai-powered-on-device-llm-infer-bootstrap"]
modifies: ["backend/model_loader.py", "backend/config.py"]
executor: glm
---
## 目标
实现从设备本地加载预训练LLM模型的机制

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
