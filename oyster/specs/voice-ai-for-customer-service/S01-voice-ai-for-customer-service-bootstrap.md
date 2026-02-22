---
task_id: S01-voice-ai-for-customer-service-bootstrap
project: voice-ai-for-customer-service
priority: 1
depends_on: []
modifies: ["backend/main.py", "backend/config.py"]
executor: glm
---
## 目标
Bootstrap voice-ai-for-customer-service: Voice AI for Customer Service

## 约束
- 实现核心功能骨架
- 写基础测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 核心模块有基础实现
- [ ] pytest 能跑通
