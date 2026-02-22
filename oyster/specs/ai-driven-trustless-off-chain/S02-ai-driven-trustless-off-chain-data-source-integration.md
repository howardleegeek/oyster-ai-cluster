---
task_id: S02-ai-driven-trustless-off-chain-data-source-integration
project: ai-driven-trustless-off-chain
priority: 1
depends_on: ["S01-ai-driven-trustless-off-chain-bootstrap"]
modifies: ["backend/data_sources.py"]
executor: glm
---
## 目标
集成多个数据源API以获取链下数据

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
