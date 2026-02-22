---
task_id: S206-voice-input
project: clawphones
priority: 2
depends_on: []
modifies: ["app/src/main/java/com/clawphones/voice/SpeechRecognizer.kt"]
executor: glm
---
## 目标
集成语音输入 STT (Speech-to-Text)

## 约束
- 在已有 Android 项目内修改
- 写单元测试
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] 单元测试全绿
- [ ] 实时语音转文字
- [ ] 支持中英文识别
- [ ] 语音输入按钮集成到聊天界面

## 不要做
- 不留 TODO/FIXME/placeholder
