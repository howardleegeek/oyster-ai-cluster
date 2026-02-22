---
task_id: S06-ai-social-network-following-system
project: ai-social-network
priority: 3
depends_on: ["S01-ai-social-network-bootstrap"]
modifies: ["backend/follows.py", "backend/main.py", "tests/test_follows.py"]
executor: glm
---
## 目标
实现用户关注功能，允许用户关注其他用户并获取关注者列表

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
