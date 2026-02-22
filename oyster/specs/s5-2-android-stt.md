## 任务: S5-2 Android 语音输入 (STT)

### 背景
Android 端也需要语音输入，使用 SpeechRecognizer API。

### 具体要求
1. 在 ChatActivity 的输入栏添加麦克风按钮
2. 使用 `android.speech.SpeechRecognizer` 实时识别
3. 识别结果实时填入输入框 (partial results)
4. 再次点击或静默停止
5. 录音时按钮变色 + 简单动画
6. 请求 `RECORD_AUDIO` 运行时权限
7. 支持中文和英文

### 文件
- 工作目录: `~/.openclaw/workspace/android/clawphones-android/`
- 主文件: `chat/ChatActivity.java` + 对应 layout XML
- AndroidManifest.xml 添加 `RECORD_AUDIO` 权限

### 验收标准
- [ ] 麦克风按钮可见
- [ ] 语音识别实时转文字
- [ ] 权限请求正常处理 (拒绝时 graceful)
- [ ] 录音状态视觉反馈
- [ ] 编译通过
