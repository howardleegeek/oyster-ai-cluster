## 任务: S5-4 语音激活 UI

### 背景
麦克风录音需要视觉反馈，让用户知道 APP 在听。

### 具体要求

#### 双端
1. 录音时在输入栏上方显示音频波形动画
2. 波形根据实际音量变化 (不是固定动画)
3. 显示录音时长计时器 "0:03"
4. 识别中的文字以灰色预览显示
5. 确认文字后变为正常颜色填入输入框

#### iOS
- 使用 `AVAudioEngine` 获取音量级别驱动动画
- SwiftUI Canvas 或自定义 Shape 绘制波形

#### Android
- 使用 `MediaRecorder.getMaxAmplitude()` 或 AudioRecord 获取音量
- 自定义 View 绘制波形

### 文件
- iOS: 新建 `VoiceWaveformView.swift`, 改 `ChatInputBar.swift`
- Android: 新建 `VoiceWaveformView.java` + layout, 改 `ChatActivity.java`

### 验收标准
- [ ] 录音时显示动态波形
- [ ] 波形随实际音量变化
- [ ] 显示录音计时
- [ ] 预览文字灰色 → 确认后正常色
- [ ] 编译通过 (双端)
