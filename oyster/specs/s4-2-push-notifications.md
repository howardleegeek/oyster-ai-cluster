## 任务: S4-2 推送通知 (FCM + APNs)

### 背景
目前无法在用户不打开 APP 时通知他们。需要推送基础设施。

### 具体要求

#### 后端 (server.py)
1. 新增 `POST /v1/user/push-token` — 注册设备推送 token
2. 数据库新增 `push_tokens` 表: (id, user_id, platform, push_token, created_at)
3. 新增内部函数 `send_push(user_id, title, body)`:
   - iOS: 通过 APNs HTTP/2 发送
   - Android: 通过 FCM HTTP v1 API 发送
4. 暂时只支持: 系统公告推送 (admin 触发)

#### Android
1. 添加 Firebase Cloud Messaging 依赖
2. 实现 `ClawPhonesMessagingService extends FirebaseMessagingService`
3. `onNewToken()` → 调用 `/v1/user/push-token` 注册
4. `onMessageReceived()` → 显示 Notification
5. 在 `build.gradle` 添加 firebase-messaging 依赖

#### iOS
1. 在 `ClawPhonesApp.swift` 请求通知权限
2. 实现 `UNUserNotificationCenterDelegate`
3. 获取 APNs token → 调用 `/v1/user/push-token` 注册
4. 处理前台/后台通知展示

### 文件
- 后端: `server.py`
- Android: 新建 `ClawPhonesMessagingService.java`, 改 `build.gradle`
- iOS: 改 `ClawPhonesApp.swift`, `OpenClawAPI.swift`

### 验收标准
- [ ] 后端 push_tokens 表创建成功
- [ ] Android/iOS 启动时注册 push token 到后端
- [ ] 后端能给指定 user_id 发推送 (可通过 admin API 测试)
- [ ] 通知在锁屏/后台显示
- [ ] 编译通过 (双端)

### 注意
- FCM 需要 `google-services.json` (已有或需要创建 Firebase 项目)
- APNs 需要 Apple Developer 证书配置
- 先实现注册和接收框架，发送端可以先用 curl 手动测试
