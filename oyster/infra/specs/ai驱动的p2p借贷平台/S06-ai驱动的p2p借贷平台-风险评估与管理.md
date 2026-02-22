---
task_id: S06-ai驱动的p2p借贷平台-风险评估与管理
project: ai驱动的p2p借贷平台
priority: 3
depends_on: ["S01-ai驱动的p2p借贷平台-bootstrap"]
modifies: ["backend/risk_assessment.py", "backend/ai_model.py", "tests/test_risk_assessment.py"]
executor: glm
---
## 目标
开发风险评估模块，利用AI分析借款人的信用风险并生成风险报告。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
