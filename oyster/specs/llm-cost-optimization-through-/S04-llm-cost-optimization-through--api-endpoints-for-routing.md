---
task_id: S04-llm-cost-optimization-through--api-endpoints-for-routing
project: llm-cost-optimization-through-
priority: 2
depends_on: ["S01-llm-cost-optimization-through--bootstrap"]
modifies: ["backend/main.py", "backend/routes/routing.py"]
executor: glm
---
## 目标
为异构路由策略添加FastAPI端点，允许用户提交任务并获取路由结果

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
