## 任务: S4-1 Token 自动刷新

### 背景
当前 auth token 30天固定过期，用户被迫重新登录。需要自动刷新机制。

### 具体要求

#### 后端 (server.py)
1. 新增 `POST /v1/auth/refresh` 端点
2. 接受 Bearer token (即将过期的)，签发新 token
3. 仅在 token 剩余有效期 < 7 天时允许刷新
4. 新 token 有效期仍为 30 天
5. 记录刷新事件到 users 表 (last_refresh_at)

#### Android
1. 在 `ClawPhonesAPI.java` 添加 refresh 方法
2. 每次 API 调用时检查 token 过期时间
3. 剩余 < 7 天 → 后台自动刷新，用户无感
4. token 已过期 → 跳转 LoginActivity

#### iOS
1. 在 `OpenClawAPI.swift` 添加 refresh 方法
2. 同样的逻辑: < 7 天自动刷新，已过期跳登录

### 文件
- 后端: `~/.openclaw/workspace/proxy/server.py`
- Android: `ClawPhonesAPI.java`
- iOS: `OpenClawAPI.swift`, `AuthViewModel.swift`

### 验收标准
- [ ] 后端 `/v1/auth/refresh` 返回新 token
- [ ] 拒绝刷新剩余 > 7 天的 token (返回 400)
- [ ] Android/iOS 在 token 快过期时自动刷新
- [ ] 过期 token 被拒绝时跳转登录页
- [ ] 编译通过 (双端)
