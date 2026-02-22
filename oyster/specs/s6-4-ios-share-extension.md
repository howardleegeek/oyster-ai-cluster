## 任务: S6-4 iOS Share Extension

### 背景
用户想从 Safari/其他 APP 分享文本到 ClawPhones 进行 AI 对话。

### 具体要求
1. 创建 Share Extension target: `ClawPhonesShare`
2. 支持接收: 纯文本、URL
3. 接收后创建新会话，预填分享内容为第一条消息
4. 自动跳转到 ClawPhones 主 APP 的该会话
5. 使用 App Groups 共享数据 (UserDefaults suite)

### 文件
- 工作目录: `~/.openclaw/workspace/ios/`
- 新建: `ClawPhonesShare/` extension target
- 改: `ClawPhones.xcodeproj` (添加 target + App Group capability)

### 验收标准
- [ ] 系统分享菜单出现 ClawPhones 选项
- [ ] 分享文本后跳转到 APP 并创建新会话
- [ ] 分享 URL 后也能正确处理
- [ ] 编译通过
- [ ] Extension 和主 APP 数据共享正常

### 注意
- App Group ID: `group.ai.clawphones.shared`
- 需要在 Xcode 中配置 App Group capability
- Share Extension 有 120MB 内存限制，保持轻量
