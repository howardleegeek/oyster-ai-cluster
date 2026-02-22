---
task_id: S05-llm-cost-optimization-through--unit-tests-for-routing
project: llm-cost-optimization-through-
priority: 2
depends_on: ["S01-llm-cost-optimization-through--bootstrap"]
modifies: ["tests/test_routing.py", "tests/test_cost_calculator.py"]
executor: glm
---
## 目标
为异构路由策略和成本估算模块编写单元测试，确保功能正确性

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
