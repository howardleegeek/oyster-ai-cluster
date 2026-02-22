---
task_id: S06-new-venture-ai-driven-decentr-testing
project: new-venture-ai-driven-decentr
priority: 3
depends_on: ["S01-new-venture-ai-driven-decentr-bootstrap"]
modifies: ["tests/test_data_ingestion.py", "tests/test_endpoints.py", "tests/test_ai_model.py"]
executor: glm
---
## 目标
编写单元测试，确保数据抓取、存储和API端点的功能正确性

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
