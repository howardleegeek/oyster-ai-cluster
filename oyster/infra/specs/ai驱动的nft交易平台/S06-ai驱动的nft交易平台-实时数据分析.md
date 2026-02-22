---
task_id: S06-ai驱动的nft交易平台-实时数据分析
project: ai驱动的nft交易平台
priority: 2
depends_on: ["S01-ai驱动的nft交易平台-bootstrap"]
modifies: ["backend/analytics.py", "backend/main.py", "tests/test_analytics.py"]
executor: glm
---
## 目标
实现实时数据分析和仪表板，展示交易量、用户活跃度等关键指标

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
