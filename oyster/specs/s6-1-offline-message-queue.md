## 任务: S6-1 离线消息队列

### 背景
断网时用户发消息直接失败，需要本地队列缓存，联网后自动重发。

### 具体要求

#### Android
1. 使用 SQLite 创建 `pending_messages` 表 (message, conversation_id, created_at, status)
2. 发送消息时: 有网 → 直接发; 无网 → 存入队列
3. 网络恢复 (BroadcastReceiver 监听 CONNECTIVITY_CHANGE) → 自动重发队列
4. 队列中的消息在 UI 显示为 "发送中..." 灰色状态
5. 重发失败 3 次 → 标记为 "发送失败" + 手动重试按钮

#### iOS
1. 使用 UserDefaults 或 FileManager 存储 pending messages (JSON 数组)
2. 使用 `NWPathMonitor` 监听网络状态
3. 同样的逻辑: 灰色 → 自动重发 → 失败后手动重试

### 文件
- Android: 新建 `MessageQueue.java`, 改 `ChatActivity.java`
- iOS: 新建 `MessageQueue.swift`, 改 `ChatViewModel.swift`

### 验收标准
- [ ] 断网发消息不报错，显示 "发送中"
- [ ] 恢复网络后自动发送
- [ ] 3 次失败后显示 "发送失败" + 重试按钮
- [ ] 编译通过 (双端)
