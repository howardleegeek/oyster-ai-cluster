---
task_id: S06-ai-driven-decentralized-financ-testing
project: ai-driven-decentralized-financ
priority: 3
depends_on: ["S01-ai-driven-decentralized-financ-bootstrap"]
modifies: ["tests/test_data_processing.py", "tests/test_ai_model.py"]
executor: glm
---
## 目标
编写单元测试，确保数据处理和AI建议生成模块的正确性

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
