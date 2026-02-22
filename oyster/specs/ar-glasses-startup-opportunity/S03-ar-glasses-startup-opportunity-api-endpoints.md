---
task_id: S03-ar-glasses-startup-opportunity-api-endpoints
project: ar-glasses-startup-opportunity
priority: 1
depends_on: ["S01-ar-glasses-startup-opportunity-bootstrap"]
modifies: ["backend/main.py", "backend/endpoints/user.py", "backend/endpoints/device.py"]
executor: glm
---
## 目标
实现基本的API端点，包括用户认证和设备管理

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
