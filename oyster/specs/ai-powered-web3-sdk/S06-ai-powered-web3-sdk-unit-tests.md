---
task_id: S06-ai-powered-web3-sdk-unit-tests
project: ai-powered-web3-sdk
priority: 3
depends_on: ["S01-ai-powered-web3-sdk-bootstrap"]
modifies: ["tests/test_wallet.py", "tests/test_contracts.py", "tests/test_events.py", "tests/test_transactions.py"]
executor: glm
---
## 目标
为Web3 SDK功能编写单元测试，确保各个模块的正确性

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
