---
task_id: S06-ai-driven-parametric-crypto-in-reporting
project: ai-driven-parametric-crypto-in
priority: 3
depends_on: ["S01-ai-driven-parametric-crypto-in-bootstrap"]
modifies: ["backend/reporting.py", "tests/test_reporting.py"]
executor: glm
---
## 目标
实现报表生成功能，生成保险业务相关的统计报表和可视化图表

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
