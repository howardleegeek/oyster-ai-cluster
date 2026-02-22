# ClawPhones Android v2 — API Integration Spec

## Status: Codex C20 dispatched (2026-02-11)

## 背景
Android 版本是 BotDrop fork (Termux-based terminal emulator)。
需要加入 AI 聊天功能，对接后端 API: http://3.142.69.6:8080

## 新增组件

### 1. LoginActivity
- 邮箱/密码登录 + 注册切换
- 密码 >= 8 字符
- Token 存 SharedPreferences
- 成功跳转 ChatActivity

### 2. ChatActivity
- RecyclerView 消息列表
- 用户气泡靠右蓝色，AI 靠左灰色
- 底部输入框 + 发送按钮
- 简单 Markdown (Html.fromHtml)

### 3. ClawPhonesAPI
- OkHttp 或 HttpURLConnection
- POST /v1/auth/register
- POST /v1/auth/login
- POST /v1/conversations
- POST /v1/conversations/{id}/chat
- GET /v1/conversations
- Authorization: Bearer {token}

### 4. AndroidManifest 改动
- usesCleartextTraffic=true
- INTERNET permission
- 注册新 Activity

## API 对接 (和 iOS 共享同一后端)
- BASE_URL: http://3.142.69.6:8080
- 注册: POST /v1/auth/register {email, password, name?} -> {user_id, token, tier}
- 登录: POST /v1/auth/login {email, password} -> {user_id, token, tier, name, ai_config}
- 创建对话: POST /v1/conversations (Bearer token) -> {id, title, created_at}
- 聊天: POST /v1/conversations/{id}/chat {message} -> {message_id, role, content}
- 对话列表: GET /v1/conversations -> {conversations: [...]}

## 编译
```bash
JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home \
ANDROID_HOME=~/Library/Android/sdk \
./gradlew assembleDebug
```
APK 输出: app/build/outputs/apk/debug/

## 后续
- SSE streaming (Android OkHttp EventSource)
- 设置页面 (用户资料、AI config、计划)
- Google Sign-In (对标 iOS Apple Sign-In)
- Material Design 3 UI 重构
