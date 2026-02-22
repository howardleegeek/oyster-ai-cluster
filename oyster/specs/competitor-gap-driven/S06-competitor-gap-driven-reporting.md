---
task_id: S06-competitor-gap-driven-reporting
project: competitor-gap-driven
priority: 2
depends_on: ["S01-competitor-gap-driven-bootstrap"]
modifies: ["backend/reporting.py", "backend/templates/"]
executor: glm
---
## 目标
开发报告生成功能，以可视化竞争对手与我们的产品差距

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
