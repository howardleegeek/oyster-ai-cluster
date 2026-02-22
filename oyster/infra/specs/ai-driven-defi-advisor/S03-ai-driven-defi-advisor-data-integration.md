---
task_id: S03-ai-driven-defi-advisor-data-integration
project: ai-driven-defi-advisor
priority: 1
depends_on: ["S01-ai-driven-defi-advisor-bootstrap"]
modifies: ["backend/data_integration.py"]
executor: glm
---
## 目标
集成外部DeFi数据源，实时获取市场数据和智能合约信息

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
