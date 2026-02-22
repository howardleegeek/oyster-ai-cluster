## 任务: S3-2 Android Settings 接通后端

### 背景
Android 有 Settings UI 但部分没有接通后端 API。iOS 的 SettingsView/AIConfigView 已完整接通，Android 需追平。

### 具体要求
1. **AI Persona 选择** — 读取/保存到 `PUT /v1/user/ai-config`
   - 预设: assistant, coder, writer, translator
   - 自定义 system prompt 输入框
2. **Language 设置** — 读取/保存到 `PUT /v1/user/profile` 的 language 字段
3. **Plan 信息展示** — 调用 `GET /v1/user/plan` 显示当前 tier + 用量
4. 确保 Settings 页面所有选项都有实际功能，移除任何空操作的菜单项

### 参考
- iOS 实现: `SettingsView.swift`, `AIConfigView.swift`, `SettingsViewModel.swift`
- 后端 API: `server.py` 搜索 `/v1/user/`
- Android API: `ClawPhonesAPI.java`

### 文件
- 工作目录: `~/.openclaw/workspace/android/clawphones-android/`
- 需要改: Settings 相关 Activity/Fragment + `ClawPhonesAPI.java`

### 验收标准
- [ ] AI Persona 选择保存后，下次聊天使用对应 system prompt
- [ ] Language 设置保存到后端
- [ ] Plan 界面显示 tier 名称 + 今日用量 / 每日上限
- [ ] 所有 Settings 菜单项都有实际功能 (无空操作)
- [ ] 编译通过
