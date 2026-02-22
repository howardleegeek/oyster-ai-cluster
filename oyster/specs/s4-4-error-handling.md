## 任务: S4-4 错误处理统一

### 背景
双端对网络错误、token 过期、服务不可用的处理不统一，用户体验差。

### 具体要求

#### Android
1. 创建统一的 `ErrorHandler.java` 工具类
2. 处理以下场景:
   - 网络不可达 → 显示 "无网络连接" banner (不是 Toast)
   - 401 Unauthorized → 清除 token → 跳转 LoginActivity
   - 429 Rate Limited → 显示 "请稍后再试" + 倒计时
   - 500 Server Error → 显示 "服务暂时不可用"
   - Timeout → 显示 "请求超时，点击重试"
3. 所有 API 调用统一走 ErrorHandler

#### iOS
1. 创建统一的 `ErrorHandler.swift`
2. 同样的场景处理
3. 用 SwiftUI `.alert()` 或 banner overlay 展示

### 文件
- Android: 新建 `ErrorHandler.java`, 修改所有 API 调用处
- iOS: 新建 `ErrorHandler.swift`, 修改 ViewModel 层

### 验收标准
- [ ] 断网时显示友好提示 (不是崩溃或空白)
- [ ] Token 过期自动跳登录
- [ ] 429 显示等待提示
- [ ] 500 显示服务不可用
- [ ] 超时有重试按钮
- [ ] 编译通过 (双端)
