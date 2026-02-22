## 任务: iOS CrashReporter (S2-5 P0)

### 背景
后端已有 POST /v1/crash-reports 端点。需要在 iOS 端实现非致命错误捕获 + 上报。
注意: iOS signal-based crash 捕获复杂且不稳定，本轮只做非致命错误上报。

### 新增文件
`ios/ClawPhones/Services/CrashReporter.swift`

### 功能要求

#### 1. CrashReporter 类
```swift
final class CrashReporter {
    static let shared = CrashReporter()
    private let fileManager = FileManager.default
    private var lastAction: String = ""

    // crash_logs 目录
    private var crashLogDir: URL {
        let docs = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let dir = docs.appendingPathComponent("crash_logs")
        if !fileManager.fileExists(atPath: dir.path) {
            try? fileManager.createDirectory(at: dir, withIntermediateDirectories: true)
        }
        return dir
    }
}
```

#### 2. 保存非致命错误
```swift
func reportNonFatal(error: Error, action: String) {
    let report: [String: Any] = [
        "platform": "ios",
        "app_version": Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "unknown",
        "device_model": UIDevice.current.model,
        "os_version": "iOS \(UIDevice.current.systemVersion)",
        "stacktrace": String(describing: error),
        "user_action": action,
        "fatal": false,
        "timestamp": Int(Date().timeIntervalSince1970)
    ]
    // 去重: 同 error.localizedDescription hash 5 分钟内不重复
    saveToFile(report)
}
```

#### 3. 保存到文件
```swift
private func saveToFile(_ report: [String: Any]) {
    let filename = "\(Int(Date().timeIntervalSince1970)).json"
    let fileURL = crashLogDir.appendingPathComponent(filename)
    if let data = try? JSONSerialization.data(withJSONObject: report) {
        try? data.write(to: fileURL)
    }
    // 限制最多 50 个文件
    cleanOldFiles()
}
```

#### 4. 上报到后端
```swift
func uploadPendingReports() {
    guard let token = UserDefaults.standard.string(forKey: "auth_token") else { return }
    // 也检查 Keychain token

    let files = (try? fileManager.contentsOfDirectory(at: crashLogDir, includingPropertiesForKeys: nil)) ?? []
    for file in files where file.pathExtension == "json" {
        guard let data = try? Data(contentsOf: file) else { continue }
        // POST to /v1/crash-reports
        Task {
            do {
                var request = URLRequest(url: URL(string: "\(OpenClawAPI.shared.baseURL)/v1/crash-reports")!)
                request.httpMethod = "POST"
                request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
                request.setValue("application/json", forHTTPHeaderField: "Content-Type")
                request.httpBody = data
                let (_, response) = try await URLSession.shared.data(for: request)
                if let http = response as? HTTPURLResponse, http.statusCode == 200 {
                    try? fileManager.removeItem(at: file)
                }
            } catch {
                // 保留文件，下次重试
            }
        }
    }
}
```

#### 5. 集成到现有代码

在 `ChatViewModel.swift` 的 catch 块中:
```swift
} catch {
    CrashReporter.shared.reportNonFatal(error: error, action: "streaming_chat")
    // 现有错误处理...
}
```

在 `OpenClawAPI.swift` 的网络错误中:
```swift
// 5xx 错误
if httpResponse.statusCode >= 500 {
    CrashReporter.shared.reportNonFatal(
        error: NSError(domain: "API", code: httpResponse.statusCode),
        action: "api_call"
    )
}
```

在 App 启动时 (ClawPhonesApp.swift 或 ContentView.swift onAppear):
```swift
CrashReporter.shared.uploadPendingReports()
```

#### 6. 用户操作追踪
```swift
func setLastAction(_ action: String) { lastAction = action }
```
在关键位置调用:
- ChatView 发送消息: `CrashReporter.shared.setLastAction("sending_message")`
- ConversationListView 加载: `CrashReporter.shared.setLastAction("loading_conversations")`

### 约束
- 不用第三方库
- crash_logs 目录上限 50 个文件
- stacktrace 截断 5000 字符
- 上报在后台线程 (Task { })
- 最低 iOS 15

### 验收标准
- [ ] API 5xx 错误自动保存到 crash_logs/
- [ ] Streaming 断开自动保存到 crash_logs/
- [ ] App 启动时自动上报 pending crash logs
- [ ] 上报成功后删除本地文件
- [ ] 编译通过: cd /Users/howardli/.openclaw/workspace/ios && xcodebuild -project ClawPhones.xcodeproj -scheme ClawPhones -sdk iphonesimulator -destination 'platform=iOS Simulator,name=iPhone 16' build 2>&1 | tail -30
