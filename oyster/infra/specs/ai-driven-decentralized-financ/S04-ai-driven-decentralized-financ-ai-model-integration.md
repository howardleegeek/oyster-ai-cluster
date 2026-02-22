---
task_id: S04-ai-driven-decentralized-financ-ai-model-integration
project: ai-driven-decentralized-financ
priority: 1
depends_on: ["S01-ai-driven-decentralized-financ-bootstrap"]
modifies: ["backend/ai_model.py", "backend/api/routes/advice.py"]
executor: glm
---
## 目标
集成预训练的AI模型，用于分析市场趋势和提供投资建议

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
