---
task_id: S04-ai-driven-defi-advisor-recommendation-engine
project: ai-driven-defi-advisor
priority: 1
depends_on: ["S01-ai-driven-defi-advisor-bootstrap"]
modifies: ["backend/recommendation_engine.py"]
executor: glm
---
## 目标
开发基于AI的推荐引擎，根据用户输入和市场数据生成投资建议

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
