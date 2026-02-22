---
task_id: S03-ai-copilot-for-consumer-defi-w-wallet-api
project: ai-copilot-for-consumer-defi-w
priority: 1
depends_on: ["S01-ai-copilot-for-consumer-defi-w-bootstrap"]
modifies: ["backend/wallet.py", "backend/main.py", "tests/test_wallet.py"]
executor: glm
---
## 目标
创建钱包相关的API端点，如创建钱包、获取钱包余额和交易历史

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
