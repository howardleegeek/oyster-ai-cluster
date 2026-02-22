---
task_id: S04-ai-contract-review-clause-detection
project: ai-contract-review
priority: 2
depends_on: ["S01-ai-contract-review-bootstrap"]
modifies: ["backend/clause_detection.py"]
executor: glm
---
## 目标
实现合同条款检测功能，识别合同中的关键条款和段落

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
