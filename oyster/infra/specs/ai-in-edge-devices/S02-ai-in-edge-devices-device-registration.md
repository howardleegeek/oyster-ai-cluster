---
task_id: S02-ai-in-edge-devices-device-registration
project: ai-in-edge-devices
priority: 1
depends_on: ["S01-ai-in-edge-devices-bootstrap"]
modifies: ["backend/device_api.py", "backend/models/device.py"]
executor: glm
---
## 目标
实现设备注册API，允许边缘设备向服务器注册自身信息

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
