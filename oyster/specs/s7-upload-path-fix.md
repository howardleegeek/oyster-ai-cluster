## 任务: 修复 S7 Upload Endpoint 路径 — 统一为 /v1/upload

### 背景
S7 image upload 实现使用了 conversation-scoped 路径 `POST /v1/conversations/{id}/upload`，但统一 API 设计需要全局 `/v1/upload` 端点。需要添加全局端点，保留 conversation-scoped 作为别名。

### 工作目录
`~/.openclaw/workspace/`

### 具体要求

1. **后端** (`proxy/server.py`):
   - 新增 `POST /v1/upload` 端点，功能与现有 conversation upload 相同
   - 参数: multipart file + optional `conversation_id` query param
   - 复用现有 upload 处理逻辑（提取为共享函数）
   - 保留 `POST /v1/conversations/{id}/upload` 作为兼容别名（调用同一函数）
   - 返回 JSON: `{"file_id": "...", "url": "/v1/files/{file_id}", "mime_type": "...", "size": int}`

2. **iOS** (`ios/ClawPhones/Services/OpenClawAPI.swift`):
   - 找到上传函数，将 URL 改为 `/v1/upload?conversation_id=\(id)`
   - 确保 multipart form data 格式不变

3. **Android** (`android/.../ClawPhonesAPI.java`):
   - 找到上传函数，将 URL 改为 `/v1/upload?conversation_id=\(id)`
   - 确保 multipart 格式不变

### 现有代码接入点
- 复用: `proxy/server.py` line ~2872 的 upload 处理逻辑
- 复用: 现有 file validation, SHA256 naming, UPLOAD_DIR 存储
- 不要碰: rate limiting (P0-3 正在改)、认证逻辑

### 验收标准
- [ ] `POST /v1/upload` 可上传文件并返回 file_id
- [ ] `POST /v1/conversations/{id}/upload` 仍然正常工作
- [ ] 双端客户端使用新 `/v1/upload` 路径
- [ ] 编译通过（Python + iOS + Android）

### 注意
- 不与 P0 security spec 冲突 — 这里只改路由，不改安全逻辑
- server.py 同时被 P0 spec 修改，注意合并冲突 — 在不同区域操作应该没问题
