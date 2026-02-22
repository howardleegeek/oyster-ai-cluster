---
task_id: S05-new-venture-ai-driven-decentr-ai-model-integration
project: new-venture-ai-driven-decentr
priority: 2
depends_on: ["S01-new-venture-ai-driven-decentr-bootstrap"]
modifies: ["backend/ai_model.py", "backend/services.py"]
executor: glm
---
## 目标
集成AI模型，用于分析DeFi数据并生成投资建议

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
