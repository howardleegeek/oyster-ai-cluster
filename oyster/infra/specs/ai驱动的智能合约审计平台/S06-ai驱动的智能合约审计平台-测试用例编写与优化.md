---
task_id: S06-ai驱动的智能合约审计平台-测试用例编写与优化
project: ai驱动的智能合约审计平台
priority: 3
depends_on: ["S01-ai驱动的智能合约审计平台-bootstrap"]
modifies: ["tests/test_parser.py", "tests/test_ai_integration.py", "tests/test_reporting.py"]
executor: glm
---
## 目标
编写和优化智能合约审计平台的测试用例，确保各模块功能正确。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
