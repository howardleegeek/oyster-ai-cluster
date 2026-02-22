---
task_id: S01-ai-social-network-bootstrap
project: ai-social-network
priority: 1
depends_on: []
modifies: ["backend/main.py", "backend/config.py"]
executor: glm
---
## 目标
Bootstrap ai-social-network: AI social network

## 约束
- 实现核心功能骨架
- 写基础测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 核心模块有基础实现
- [ ] pytest 能跑通
