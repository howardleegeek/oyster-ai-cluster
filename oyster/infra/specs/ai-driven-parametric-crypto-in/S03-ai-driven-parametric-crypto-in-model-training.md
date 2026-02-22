---
task_id: S03-ai-driven-parametric-crypto-in-model-training
project: ai-driven-parametric-crypto-in
priority: 2
depends_on: ["S01-ai-driven-parametric-crypto-in-bootstrap"]
modifies: ["backend/model_training.py", "tests/test_model_training.py"]
executor: glm
---
## 目标
开发AI模型训练脚本，使用历史市场数据训练预测模型

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
