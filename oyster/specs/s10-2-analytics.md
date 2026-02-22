## 任务: S10-2 基础 Analytics

### 背景
需要了解用户行为以优化产品。轻量级实现，不依赖第三方 SDK。

### 具体要求

#### 后端
1. 新增 `POST /v1/analytics/events` 端点
2. 接受事件数组: [{"event": "chat_sent", "properties": {...}, "timestamp": ...}]
3. 存入 `analytics_events` 表
4. 预定义事件:
   - `app_open` — APP 打开
   - `chat_sent` — 发送消息
   - `chat_received` — 收到回复
   - `voice_used` — 使用语音
   - `conversation_created` — 新建会话
   - `settings_changed` — 修改设置

#### 双端
1. 创建 `Analytics.swift` / `Analytics.java` 单例
2. `Analytics.track("event_name", properties)` 方法
3. 事件先缓存本地，每 5 分钟批量上传
4. 在关键位置埋点 (上面列出的事件)

### 文件
- 后端: `server.py`
- iOS: 新建 `Analytics.swift`
- Android: 新建 `Analytics.java`

### 验收标准
- [ ] 后端接收和存储事件
- [ ] 双端在关键路径埋点
- [ ] 批量上传减少网络请求
- [ ] 不影响 APP 性能
- [ ] 编译通过 (双端)
