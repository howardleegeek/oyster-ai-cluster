## 任务: S7-1 图片上传与 AI 识图

### 背景
用户需要发送图片让 AI 分析 (vision capability)。后端已支持多模型，需要双端支持图片输入。

### 具体要求

#### 后端 (server.py)
1. 新增 `POST /v1/upload` 端点 — 接收 multipart 图片，存储到本地 `uploads/` 目录
2. 返回 `{"url": "/uploads/{id}.jpg"}`
3. 修改 chat/stream 端点: messages 支持 `content` 为数组格式 (OpenAI vision format):
   ```json
   {"role":"user","content":[{"type":"text","text":"..."}, {"type":"image_url","url":"..."}]}
   ```
4. 上传限制: 最大 10MB, 仅 jpg/png/gif/webp

#### Android
1. 在 ChatActivity 输入栏添加图片按钮 (相册选择 + 拍照)
2. 选择后压缩到 1MB 以内 → 上传到 `/v1/upload`
3. 上传完成后发送带 image_url 的消息
4. 在消息列表中显示图片缩略图

#### iOS
1. 在 ChatInputBar 添加图片按钮
2. 使用 `PhotosPicker` (iOS 16+) 选择图片
3. 同样压缩 + 上传 + 发送
4. MessageRow 中显示图片

### 文件
- 后端: `server.py`
- Android: `ChatActivity.java` + layout
- iOS: `ChatInputBar.swift`, `ChatViewModel.swift`, `MessageRow.swift`

### 验收标准
- [ ] 选择/拍照图片 → 上传 → AI 返回图片分析
- [ ] 图片在聊天中显示缩略图
- [ ] 大图压缩到合理大小
- [ ] 非图片文件拒绝上传
- [ ] 编译通过 (双端)
