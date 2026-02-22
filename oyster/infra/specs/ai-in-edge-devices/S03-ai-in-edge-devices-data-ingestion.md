---
task_id: S03-ai-in-edge-devices-data-ingestion
project: ai-in-edge-devices
priority: 1
depends_on: ["S01-ai-in-edge-devices-bootstrap"]
modifies: ["backend/data_api.py", "backend/schemas/data.py"]
executor: glm
---
## 目标
开发数据摄取接口，用于接收来自边缘设备的数据流

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
