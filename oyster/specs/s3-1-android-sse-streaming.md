## 任务: S3-1 Android SSE 流式聊天

### 背景
ClawPhones Android 目前只有 sync 聊天（等全部生成完才显示），iOS 已有 SSE 流式。Android 需要追平。

### 具体要求
1. 在 `ChatActivity.java` (chat/ 包下的新版，611行) 中接入 SSE 流式响应
2. 调用后端 `POST /v1/conversations/{id}/chat/stream` 端点
3. 解析 OpenAI-compatible SSE 格式: `data: {"choices":[{"delta":{"content":"..."}}]}`
4. 实时逐字显示 AI 回复，不要等全部完成
5. 处理 `[DONE]` 信号结束流
6. 保留 sync fallback: 如果 SSE 连接失败，自动降级到 sync `/chat` 端点
7. 流式过程中显示 typing indicator，完成后替换为完整消息

### 参考
- iOS 实现: `~/.openclaw/workspace/ios/ClawPhones/ViewModels/ChatViewModel.swift` (SSE 解析逻辑)
- 后端端点: `~/.openclaw/workspace/proxy/server.py` 搜索 `/chat/stream`
- Android API 客户端: `ConversationApiClient.java`

### 文件
- 工作目录: `~/.openclaw/workspace/android/clawphones-android/`
- 主文件: `app/src/main/java/ai/clawphones/agent/chat/ChatActivity.java`
- API 客户端: `app/src/main/java/ai/clawphones/agent/ConversationApiClient.java`

### 验收标准
- [ ] 发送消息后 AI 回复逐字出现 (不是等全部完成)
- [ ] SSE 断开时自动 fallback 到 sync
- [ ] 流式过程中有 typing indicator
- [ ] `[DONE]` 后消息完整保存到 conversation
- [ ] 编译通过
- [ ] 不使用第三方 SSE 库 (用 OkHttp/HttpURLConnection 手动解析即可)
