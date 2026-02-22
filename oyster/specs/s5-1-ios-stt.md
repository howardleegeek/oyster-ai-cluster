## 任务: S5-1 iOS 语音输入 (STT)

### 背景
AI 助手需要语音输入。iOS 有原生 Speech framework。

### 具体要求
1. 在 `ChatInputBar.swift` 添加麦克风按钮 (发送按钮左侧)
2. 点击开始录音，使用 `SFSpeechRecognizer` 实时转文字
3. 识别结果实时填入输入框
4. 再次点击或静默 2 秒自动停止
5. 录音时麦克风按钮变红 + 简单脉冲动画
6. 首次使用请求麦克风 + 语音识别权限
7. 支持中文和英文 (根据系统语言或 APP 设置的 language)

### 文件
- 工作目录: `~/.openclaw/workspace/ios/`
- 主文件: `ClawPhones/Views/ChatInputBar.swift`
- Info.plist 需要: `NSSpeechRecognitionUsageDescription`, `NSMicrophoneUsageDescription`

### 验收标准
- [ ] 麦克风按钮可见且位置合理
- [ ] 点击后开始语音识别，文字实时出现在输入框
- [ ] 静默 2 秒自动停止
- [ ] 录音状态有视觉反馈 (红色 + 动画)
- [ ] 权限弹窗正常
- [ ] 编译通过
