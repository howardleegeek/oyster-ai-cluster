---
task_id: S05-ai-agent-for-on-device-process-set-up-authentication
project: ai-agent-for-on-device-process
priority: 2
depends_on: ["S01-ai-agent-for-on-device-process-bootstrap"]
modifies: ["backend/auth.py", "backend/main.py"]
executor: glm
---
## 目标
设置基础的认证机制（如 JWT）以保护 API 端点

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
