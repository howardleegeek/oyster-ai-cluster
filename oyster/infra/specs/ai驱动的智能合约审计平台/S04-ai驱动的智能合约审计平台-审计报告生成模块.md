---
task_id: S04-ai驱动的智能合约审计平台-审计报告生成模块
project: ai驱动的智能合约审计平台
priority: 2
depends_on: ["S01-ai驱动的智能合约审计平台-bootstrap"]
modifies: ["backend/reporting.py", "backend/templates/"]
executor: glm
---
## 目标
开发审计报告生成模块，根据AI检测结果生成详细的审计报告。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
