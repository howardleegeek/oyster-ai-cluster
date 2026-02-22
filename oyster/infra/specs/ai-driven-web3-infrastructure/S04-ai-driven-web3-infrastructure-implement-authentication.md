---
task_id: S04-ai-driven-web3-infrastructure-implement-authentication
project: ai-driven-web3-infrastructure
priority: 2
depends_on: ["S01-ai-driven-web3-infrastructure-bootstrap"]
modifies: ["backend/auth.py", "backend/main.py", "tests/test_auth.py"]
executor: glm
---
## 目标
实现用户认证和授权机制

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
