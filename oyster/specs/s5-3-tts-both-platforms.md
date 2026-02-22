## 任务: S5-3 双端文字转语音 (TTS)

### 背景
AI 回复可以朗读出来，提升无障碍和免提使用体验。

### 具体要求

#### iOS
1. 在 `MessageRow.swift` 的 AI 消息气泡上添加小喇叭图标
2. 点击使用 `AVSpeechSynthesizer` 朗读该消息
3. 朗读中图标变为 "停止" 图标，点击停止
4. 自动检测语言 (中/英)

#### Android
1. 在 ChatActivity 的消息 item 上添加喇叭图标 (AI 消息才显示)
2. 使用 `android.speech.tts.TextToSpeech` 朗读
3. 同样支持播放/停止切换
4. 自动检测语言

### 文件
- iOS: `MessageRow.swift`
- Android: `chat/ChatActivity.java` + message item layout

### 验收标准
- [ ] AI 消息有喇叭按钮
- [ ] 点击朗读，再点停止
- [ ] 中英文自动识别
- [ ] 朗读完成后图标恢复
- [ ] 编译通过 (双端)
