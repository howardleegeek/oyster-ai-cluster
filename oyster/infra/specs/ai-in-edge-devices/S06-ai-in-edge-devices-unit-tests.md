---
task_id: S06-ai-in-edge-devices-unit-tests
project: ai-in-edge-devices
priority: 3
depends_on: ["S01-ai-in-edge-devices-bootstrap"]
modifies: ["tests/test_device_api.py", "tests/test_data_api.py"]
executor: glm
---
## 目标
为设备注册和数据摄取接口编写单元测试，确保功能正确性

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
