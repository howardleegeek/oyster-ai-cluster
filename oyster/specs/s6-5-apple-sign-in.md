## 任务: S6-5 Apple Sign In

### 背景
后端 users 表已有 `apple_id` 字段，但 OAuth 流程未实现。App Store 上架要求支持 Apple Sign In。

### 具体要求

#### 后端 (server.py)
1. 新增 `POST /v1/auth/apple` 端点
2. 接受 Apple identity token (JWT)
3. 验证 JWT: 从 Apple 公钥 (`https://appleid.apple.com/auth/keys`) 验签
4. 提取 `sub` (Apple user ID) + email
5. 如果 apple_id 已存在 → 登录; 不存在 → 自动注册
6. 返回 auth token (同 /v1/auth/login 格式)

#### iOS
1. 在 LoginView 添加 "Sign in with Apple" 按钮 (ASAuthorizationAppleIDButton)
2. 使用 AuthenticationServices framework
3. 获取 identity token → 发送到 `/v1/auth/apple`
4. 成功后存 token 到 Keychain，进入主界面
5. 处理: 用户拒绝、Apple ID 未配置等错误

### 文件
- 后端: `server.py` (新增 /v1/auth/apple 端点)
- iOS: `LoginView.swift`, `AuthViewModel.swift`, `OpenClawAPI.swift`

### 验收标准
- [ ] 后端验证 Apple JWT 并返回 auth token
- [ ] iOS "Sign in with Apple" 按钮符合 Apple HIG
- [ ] 首次登录自动创建账号
- [ ] 第二次登录匹配已有账号
- [ ] 用户拒绝授权时 graceful 处理
- [ ] 编译通过

### 注意
- 需要 Apple Developer 配置 Sign in with Apple capability
- 测试时可能需要真机 (模拟器有限制)
- PyJWT 库验证 Apple JWT (pip install PyJWT cryptography)
