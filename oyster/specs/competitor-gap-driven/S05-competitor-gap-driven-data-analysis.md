---
task_id: S05-competitor-gap-driven-data-analysis
project: competitor-gap-driven
priority: 2
depends_on: ["S01-competitor-gap-driven-bootstrap"]
modifies: ["backend/analysis.py"]
executor: glm
---
## 目标
实现数据分析模块以识别竞争对手与我们的产品差距

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
