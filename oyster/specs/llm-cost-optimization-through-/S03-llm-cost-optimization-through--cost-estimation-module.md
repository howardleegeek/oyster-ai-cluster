---
task_id: S03-llm-cost-optimization-through--cost-estimation-module
project: llm-cost-optimization-through-
priority: 1
depends_on: ["S01-llm-cost-optimization-through--bootstrap"]
modifies: ["backend/cost_calculator.py"]
executor: glm
---
## 目标
开发成本估算模块，根据不同的LLM模型和路由策略预估计算成本

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
