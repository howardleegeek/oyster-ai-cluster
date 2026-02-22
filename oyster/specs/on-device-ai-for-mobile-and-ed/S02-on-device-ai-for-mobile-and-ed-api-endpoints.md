---
task_id: S02-on-device-ai-for-mobile-and-ed-api-endpoints
project: on-device-ai-for-mobile-and-ed
priority: 1
depends_on: ["S01-on-device-ai-for-mobile-and-ed-bootstrap"]
modifies: ["backend/main.py", "backend/routers/ai_requests.py"]
executor: glm
---
## 目标
设计并实现FastAPI的API端点，用于接收和处理来自移动和边缘设备的AI请求

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
