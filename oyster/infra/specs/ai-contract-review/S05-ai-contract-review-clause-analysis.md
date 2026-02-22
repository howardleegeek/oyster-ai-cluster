---
task_id: S05-ai-contract-review-clause-analysis
project: ai-contract-review
priority: 2
depends_on: ["S01-ai-contract-review-bootstrap"]
modifies: ["backend/clause_analysis.py"]
executor: glm
---
## 目标
实现合同条款分析功能，评估条款的风险和合规性

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
