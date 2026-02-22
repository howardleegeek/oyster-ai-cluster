---
task_id: S03-新方向-ai驱动的web3交易助手-实现用户注册和认证
project: 新方向-ai驱动的web3交易助手
priority: 1
depends_on: ["S01-新方向-ai驱动的web3交易助手-bootstrap"]
modifies: ["backend/auth.py", "backend/main.py"]
executor: glm
---
## 目标
实现用户注册、登录和认证功能，确保用户数据的安全性。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
