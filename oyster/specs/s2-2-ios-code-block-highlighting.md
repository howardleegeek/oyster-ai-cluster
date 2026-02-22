## 任务: S2-2 iOS 代码块语法高亮

### 背景
ClawPhones iOS 端使用 SwiftUI 原生 `AttributedString(markdown:)` 渲染 Markdown，但代码块没有语法高亮。AI 聊天场景经常返回代码，需要高亮显示。

### 具体要求
1. 在 `MessageRow.swift` 中增加代码块检测和高亮渲染
2. 推荐方案: 使用 `swift-markdown-ui` (gonzalezreal/swift-markdown-ui) 或类似 SPM 库
3. 如果不加外部依赖，可以用正则匹配 ` ```lang ... ``` ` 块 + 手动着色
4. 最低要求: 代码块有深色背景 + 等宽字体 + 基础关键字着色 (Swift/Python/JS)
5. 不影响非代码 Markdown 的现有渲染

### 文件
- 工作目录: `~/.openclaw/workspace/ios/`
- 主文件: `ClawPhones/Views/MessageRow.swift` (line 85-98 现有 markdown 逻辑)
- 相关: `ClawPhones/Views/ChatView.swift`
- 项目文件: `ClawPhones.xcodeproj`

### 验收标准
- [ ] 代码块显示: 深色背景 + 等宽字体
- [ ] 至少 Swift/Python/JavaScript 关键字有颜色区分
- [ ] 非代码 Markdown (粗体/斜体/链接) 渲染不受影响
- [ ] 长代码块可水平滚动
- [ ] 编译通过

### 注意
- 项目当前无 SPM/CocoaPods 依赖，如果加库需要配置 Package Dependencies
- iOS 最低版本检查 deployment target (可能是 iOS 16+)
- 避免用 WKWebView 方案，保持 native SwiftUI
