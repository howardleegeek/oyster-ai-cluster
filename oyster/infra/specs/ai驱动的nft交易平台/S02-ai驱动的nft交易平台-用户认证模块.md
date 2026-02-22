---
task_id: S02-ai驱动的nft交易平台-用户认证模块
project: ai驱动的nft交易平台
priority: 1
depends_on: ["S01-ai驱动的nft交易平台-bootstrap"]
modifies: ["backend/auth.py", "backend/main.py", "tests/test_auth.py"]
executor: glm
---
## 目标
实现用户注册、登录和身份验证功能，包括JWT token生成和验证

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
