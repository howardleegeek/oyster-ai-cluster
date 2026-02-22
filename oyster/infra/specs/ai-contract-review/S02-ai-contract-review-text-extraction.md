---
task_id: S02-ai-contract-review-text-extraction
project: ai-contract-review
priority: 1
depends_on: ["S01-ai-contract-review-bootstrap"]
modifies: ["backend/text_extraction.py"]
executor: glm
---
## 目标
实现合同文本提取功能，从上传的合同文件中提取文本内容

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
