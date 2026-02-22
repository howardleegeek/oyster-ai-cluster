---
task_id: S04-ai-in-edge-devices-authentication
project: ai-in-edge-devices
priority: 2
depends_on: ["S01-ai-in-edge-devices-bootstrap"]
modifies: ["backend/authentication.py", "backend/main.py"]
executor: glm
---
## 目标
为API端点添加身份验证机制，确保只有授权设备可以访问

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
