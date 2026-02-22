## 任务: S6-2 会话本地缓存

### 背景
每次打开 APP 都要从服务器拉会话列表和历史消息，慢且费流量。需要本地缓存。

### 具体要求

#### Android
1. 使用 SQLite 缓存 conversations 和 messages 表
2. 打开 APP → 先显示缓存数据 → 后台拉最新 → 增量更新
3. 进入会话 → 先显示缓存消息 → 后台同步新消息
4. 缓存策略: 最近 50 个会话 + 每个会话最近 100 条消息

#### iOS
1. 使用 Core Data 或 FileManager JSON 缓存
2. 同样的 cache-first + background-refresh 策略

### 文件
- Android: 新建 `ConversationCache.java`, 改 List/Chat Activity
- iOS: 新建 `ConversationCache.swift`, 改 ViewModels

### 验收标准
- [ ] 断网时仍能查看历史会话和消息
- [ ] 联网时后台静默同步
- [ ] 缓存大小有上限 (50 会话 × 100 消息)
- [ ] 新消息正确追加到缓存
- [ ] 编译通过 (双端)
