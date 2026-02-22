---
task_id: S06-ai-driven-trustless-off-chain-tests
project: ai-driven-trustless-off-chain
priority: 3
depends_on: ["S01-ai-driven-trustless-off-chain-bootstrap"]
modifies: ["tests/test_data_sources.py", "tests/test_verification.py", "tests/test_endpoints.py"]
executor: glm
---
## 目标
编写单元测试以确保各个模块的功能正确性

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
