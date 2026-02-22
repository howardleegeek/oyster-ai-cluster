---
task_id: S06-ai-contract-review-report-generation
project: ai-contract-review
priority: 3
depends_on: ["S01-ai-contract-review-bootstrap"]
modifies: ["backend/report_generation.py"]
executor: glm
---
## 目标
实现合同审查报告生成功能，生成包含审查结果的报告

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
