---
task_id: S02-llm-cost-optimization-through--routing-strategy-implementation
project: llm-cost-optimization-through-
priority: 1
depends_on: ["S01-llm-cost-optimization-through--bootstrap"]
modifies: ["backend/routing.py"]
executor: glm
---
## 目标
实现异构路由策略，根据LLM模型的复杂度和资源需求动态分配计算任务

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
