---
task_id: S03-voice-ai-for-customer-service-intent-detection
project: voice-ai-for-customer-service
priority: 1
depends_on: ["S01-voice-ai-for-customer-service-bootstrap"]
modifies: ["backend/intent_detection.py"]
executor: glm
---
## 目标
实现意图检测功能，解析客户语音文本以识别客户需求。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
