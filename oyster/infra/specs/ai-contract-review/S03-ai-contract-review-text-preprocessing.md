---
task_id: S03-ai-contract-review-text-preprocessing
project: ai-contract-review
priority: 1
depends_on: ["S01-ai-contract-review-bootstrap"]
modifies: ["backend/text_preprocessing.py"]
executor: glm
---
## 目标
实现合同文本预处理功能，包括分词、去除停用词和标准化文本

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
