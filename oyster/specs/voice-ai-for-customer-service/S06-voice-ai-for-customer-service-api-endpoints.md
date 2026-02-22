---
task_id: S06-voice-ai-for-customer-service-api-endpoints
project: voice-ai-for-customer-service
priority: 1
depends_on: ["S01-voice-ai-for-customer-service-bootstrap"]
modifies: ["backend/main.py", "backend/endpoints.py"]
executor: glm
---
## 目标
创建FastAPI端点以支持语音上传、意图检测和回复获取。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
