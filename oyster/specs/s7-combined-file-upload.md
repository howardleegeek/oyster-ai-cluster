## 任务: S7-1+S7-2 图片上传 + 文件分享 (合并任务)

### 背景
用户需要在聊天中发送图片 (AI vision 分析) 和文档 (PDF/TXT 等文本提取)。
之前多次实现失败 — 代码修改未持久化到磁盘。本次必须在每个文件修改后用 `cat` 命令验证。

### 架构决策
- **文件存储**: 本地 `./data/uploads/` 目录，文件名用 SHA256 哈希防路径穿越
- **数据库**: 新增 `conversation_files` 表存文件元数据
- **消息格式**: 扩展现有 message body，加 `file_ids` 数组
- **Vision 调用**: OpenAI vision format — content 为数组包含 text + image_url
- **文本提取**: PDF 用 PyPDF2，其他纯文本直接读

### ⚠️ 关键: 文件持久化验证 (每个文件修改后必须执行)
```
修改文件后 → 立即运行 cat <文件路径> | grep "<关键函数名或路由>"
验证输出包含你刚写的代码 → 才能继续下一步
如果 cat 显示旧内容 → 重新写入，直到 cat 确认成功
```

---

### 第一步: 后端 (proxy/server.py)

#### 1.1 新增依赖 (文件顶部 imports 区域)
```python
import hashlib
import mimetypes
from pathlib import Path
```
不要 import PyPDF2 — 用 try/except 做可选依赖。

#### 1.2 新增文件存储配置 (在 EXPORT_DIR 定义附近, ~line 93)
```python
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10MB
MAX_FILE_SIZE = 20 * 1024 * 1024    # 20MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_FILE_TYPES = {"application/pdf", "text/plain", "text/csv", "application/json", "text/markdown"}
```

#### 1.3 新增 conversation_files 表 (在 init_db 函数中)
```sql
CREATE TABLE IF NOT EXISTS conversation_files (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    original_name TEXT NOT NULL,
    stored_path TEXT NOT NULL,
    sha256_hash TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    extracted_text TEXT,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

#### 1.4 新增上传端点
位置: 在 chat endpoint 之前添加

```
POST /v1/conversations/<conversation_id>/upload
```
- 接收 multipart/form-data，字段名 `file`
- 验证: conversation_id 存在 (查 conversations 表)、文件大小、MIME 类型
- 存储: SHA256(内容) 作为文件名，保留原扩展名 → `data/uploads/{sha256}.{ext}`
- 文本提取:
  - PDF → try PyPDF2, except → 存空字符串
  - text/plain, text/csv, text/markdown, application/json → 直接 `.read().decode('utf-8', errors='replace')[:50000]`
- 图片: extracted_text 为 null
- 返回:
```json
{
  "file_id": "uuid",
  "filename": "original.pdf",
  "mime_type": "application/pdf",
  "size": 12345,
  "extracted_text": "..."  // 仅文本文件
}
```

#### 1.5 新增文件获取端点
```
GET /v1/files/<file_id>
```
- 查 conversation_files 表 → 返回文件内容 (send_file)
- 需要认证 (复用现有 auth 装饰器)

#### 1.6 修改 chat/stream 端点 (lines 2452-2650)
当前请求体: `{"message": "text"}`
新请求体: `{"message": "text", "file_ids": ["id1", "id2"]}` (file_ids 可选)

修改逻辑:
1. 解析 `file_ids` (默认空列表)
2. 查 conversation_files 表获取文件信息
3. 构建 OpenAI messages:
   - 有图片 → content 改为数组格式:
     ```json
     [{"type": "text", "text": "用户消息"}, {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}]
     ```
   - 有文本文件 → 在 text 前插入提取的文本:
     ```
     [File: document.pdf]\n{extracted_text}\n\n用户消息
     ```
4. 消息入库时 content 字段存原始 text，file_ids 作为 JSON 存在 content 前缀 (或用 metadata 字段)

**验证**: 修改后运行
```bash
cat proxy/server.py | grep -n "upload\|conversation_files\|file_ids\|UPLOAD_DIR" | head -20
```

---

### 第二步: Android (ChatActivity.java + ClawPhonesAPI.java)

#### 2.1 ChatActivity.java — 添加图片/文件按钮
位置: `mSend` 按钮初始化附近 (~line 202)

1. 在 send 按钮左侧添加 attach 按钮 (ImageButton)
2. 点击弹出选择: "拍照" / "相册" / "文件"
3. 使用 ActivityResultLauncher:
   - 相册: `PickVisualMedia` (AndroidX Activity 1.7+) 或 `Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI)`
   - 拍照: `Intent(MediaStore.ACTION_IMAGE_CAPTURE)` + FileProvider
   - 文件: `Intent(Intent.ACTION_OPEN_DOCUMENT)` with MIME types

4. 选择后:
   - 图片: 压缩到 maxWidth 1024px, quality 80 → `ByteArrayOutputStream`
   - 文件: 直接读 InputStream
   - 调用 `ClawPhonesAPI.uploadFile()` → 获取 file_id
   - 在输入框上方显示附件预览 (缩略图/文件图标 + 文件名)
   - 用户点发送时带上 file_ids

5. `onSend()` 修改 (~line 555): 如果有 pending file_ids → 传给 `sendMessageOnline()`

6. `sendMessageOnline()` 修改 (~line 591): 已有 `imageUrl` 参数 → 改为 `List<String> fileIds`

#### 2.2 ClawPhonesAPI.java — 新增上传方法
```java
public static void uploadFile(Context context, String conversationId,
    byte[] fileData, String filename, String mimeType, UploadCallback callback)
```
- 用 `HttpURLConnection` 发 multipart/form-data
- POST 到 `/v1/conversations/{conversationId}/upload`
- callback 返回 file_id

#### 2.3 ClawPhonesAPI.java — 修改 chatStream()
- 方法签名加 `List<String> fileIds` 参数
- JSON body: `{"message": text, "file_ids": fileIds}`

#### 2.4 消息显示 — ChatAdapter 或 MessageViewHolder
- 如果消息有图片 → 显示缩略图 (300dp max width), 点击全屏 (新 Activity 或 Dialog)
- 如果消息有文件 → 显示文件卡片 (图标 + 文件名 + 大小)

**验证**:
```bash
cat android/clawphones-android/app/src/main/java/ai/clawphones/agent/chat/ChatActivity.java | grep -n "uploadFile\|fileIds\|ACTION_PICK\|attach" | head -10
cat android/clawphones-android/app/src/main/java/ai/clawphones/agent/chat/ClawPhonesAPI.java | grep -n "uploadFile\|file_ids\|multipart" | head -10
```

---

### 第三步: iOS (ChatInputBar + ChatViewModel + OpenClawAPI)

#### 3.1 ChatInputBar.swift — 添加附件按钮
位置: send 按钮左侧 (~line 52-61)

1. 添加 attach 按钮 (paperclip icon `systemName: "paperclip"`)
2. 点击弹出 `.confirmationDialog`: "Photo Library" / "Camera" / "File"
3. Photo Library: `PhotosPicker` (PhotosUI, iOS 16+)
4. Camera: UIImagePickerController wrapped
5. File: `.fileImporter(isPresented:, allowedContentTypes:)`

#### 3.2 ChatViewModel.swift — 添加文件处理
1. 新增 `@Published var pendingFiles: [PendingFile] = []`
2. `PendingFile` struct: `id, data, filename, mimeType, thumbnail`
3. 新增 `func uploadFile(data: Data, filename: String, mimeType: String) async -> String?` → 调用 API → 返回 file_id
4. 修改 `sendMessage(text:)` → `sendMessage(text:, fileIds:)`
5. 发送前 upload 所有 pending files → 收集 file_ids → 发消息

#### 3.3 OpenClawAPI.swift — 新增上传 + 修改 chat
1. 新增:
```swift
func uploadFile(conversationId: String, fileData: Data, filename: String, mimeType: String) async throws -> UploadResponse
```
- 构建 multipart/form-data request
- POST 到 `/v1/conversations/{conversationId}/upload`

2. 修改 `chat()` 和 `chatStream()`:
- `ChatRequestBody` 加 `fileIds: [String]?`
- 编码到 JSON body

#### 3.4 MessageRow.swift — 文件显示
- 图片消息: AsyncImage 缩略图 (300pt), 点击全屏
- 文件消息: HStack { FileIcon + filename + size }

**验证**:
```bash
cat ios/ClawPhones/Views/ChatInputBar.swift | grep -n "attach\|PhotosPicker\|fileImporter\|pendingFiles" | head -10
cat ios/ClawPhones/Services/OpenClawAPI.swift | grep -n "uploadFile\|file_ids\|multipart" | head -10
```

---

### 现有代码接入点 (精确位置)
- **复用**: `ClawPhonesAPI.doPost()` (Android), `OpenClawAPI.shared` (iOS), 现有 auth 装饰器 (Python)
- **修改**:
  - `server.py` init_db() — 加表
  - `server.py` chat/stream handler (~line 2452/2571) — 加 file_ids 解析
  - `ChatActivity.java` onSend() (~line 555) — 加文件逻辑
  - `ChatActivity.java` sendMessageOnline() (~line 591) — imageUrl → fileIds
  - `ClawPhonesAPI.java` chatStream() (~line 530) — 加 fileIds 参数
  - `ChatInputBar.swift` body (~line 52) — 加按钮
  - `ChatViewModel.swift` sendMessage() (~line 140) — 加文件参数
  - `OpenClawAPI.swift` chatStream() (~line 414) — 扩展 body
- **不要碰**: HEARTBEAT.md, CLAUDE.md, 任何 build 配置文件

### 边界情况
- 网络失败: 上传失败 → 提示用户重试，不发消息
- 超大文件: 前端预检大小，后端二次校验
- 并发上传: 一次只允许 3 个文件同时上传
- 不支持的类型: 弹 toast/alert，不发请求
- 图片压缩失败: 降级到原图 (如果在限制内) 或报错

### 安全要求
- SHA256 文件名防路径穿越
- MIME 类型白名单 (不信任 Content-Type header, 用 magic bytes 检测)
- 文件大小双重检查 (前端 + 后端)
- 不存储可执行文件
- 上传目录不在 web root 下
- file_id 用 UUID，不可猜测

### 验收标准
- [ ] 后端: POST /v1/conversations/{id}/upload 返回 file_id
- [ ] 后端: GET /v1/files/{id} 返回文件内容
- [ ] 后端: chat/stream 接受 file_ids 并正确构建 vision/text context
- [ ] Android: 可选择图片/文件，上传，发送
- [ ] Android: 聊天中显示图片缩略图和文件卡片
- [ ] iOS: 可选择图片/文件，上传，发送
- [ ] iOS: 聊天中显示图片缩略图和文件卡片
- [ ] 编译通过 (双端)
- [ ] 非法文件类型被拒绝
- [ ] 超大文件被拒绝

### 测试要求
- [ ] pytest: upload 成功/超限/格式错误/路径穿越
- [ ] pytest: chat with file_ids 构建正确 messages 格式
- [ ] 手动验证: cat 每个修改文件确认代码存在

### 注意
- **这是第 4 次尝试此任务**。前 3 次都因代码未持久化失败。
- **每改一个文件 → 立刻 cat 验证 → 确认后才继续下一个文件**
- server.py 很大 (3217 行)，修改时用精确行号定位，不要重写整个文件
- Android 已有 imageUrl 参数骨架 (sendMessageOnline line 594)，复用它
