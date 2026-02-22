---
task_id: S02-voice-ai-for-customer-service-speech-recognition
project: voice-ai-for-customer-service
priority: 1
depends_on: ["S01-voice-ai-for-customer-service-bootstrap"]
modifies: ["backend/speech_recognition.py"]
executor: glm
---
## 目标
集成语音识别模块，将客户语音转换为文本。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
