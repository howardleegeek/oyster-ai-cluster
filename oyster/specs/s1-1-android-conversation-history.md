## 任务: Android 对话历史列表页

### 背景
当前 Android ChatActivity 每次启动都创建新对话，用户无法查看或恢复历史对话。后端已有完整的 conversations CRUD API，只需前端实现。

### 后端 API（已存在，直接调用）
```
GET    /v1/conversations              → [{id, title, created_at, updated_at, message_count}, ...]
POST   /v1/conversations              → {id, title, created_at}
DELETE /v1/conversations/{id}         → 204
GET    /v1/conversations/{id}/messages → [{id, role, content, created_at}, ...]
```
所有请求需 `Authorization: Bearer <token>` header。

### 具体要求

#### 1. 新增 ConversationListActivity
- 文件: `app/src/main/java/ai/clawphones/agent/chat/ConversationListActivity.java`
- 布局: `app/src/main/res/layout/activity_conversation_list.xml`
- 页面结构:
  - Toolbar: 标题 "ClawPhones"，右侧 logout 图标按钮
  - RecyclerView: 对话列表
  - FloatingActionButton: 右下角 "+" 新建对话
  - 空状态: 居中显示 "暂无对话\n点击 + 开始聊天"

#### 2. 对话列表 item 布局
- 文件: `app/src/main/res/layout/item_conversation.xml`
- 每行显示:
  - 标题 (title，无标题时显示 "新对话")
  - 消息数量 badge (message_count)
  - 更新时间 (updated_at，格式: "今天 14:30" / "昨天" / "2月10日")
- 左滑删除 (ItemTouchHelper.SimpleCallback, swipe LEFT)
  - 删除前弹 AlertDialog 确认: "确定删除这个对话吗？"
  - 确认后调 DELETE API，移除 item

#### 3. ClawPhonesAPI 新增方法
- `static List<Map<String,Object>> getConversations(String token)` — GET /v1/conversations
- `static void deleteConversation(String token, String conversationId)` — DELETE
- `static List<Map<String,Object>> getMessages(String token, String conversationId)` — GET messages

#### 4. 导航修改
- LoginActivity 登录成功 → 跳转 ConversationListActivity（不再直接到 ChatActivity）
- ConversationListActivity 点击某对话 → ChatActivity，传 `conversation_id` extra
- ConversationListActivity 点击 FAB → ChatActivity，不传 id（ChatActivity 自动创建新对话）
- ChatActivity 返回 → ConversationListActivity（toolbar back button）

#### 5. ChatActivity 修改
- 接收 `conversation_id` extra:
  - 有值: 加载该对话历史消息 (GET /messages)，渲染到 RecyclerView
  - 无值: 创建新对话（保持现有逻辑）
- 新增 `loadHistory(conversationId)`: 调 getMessages API，按时间排序渲染
- toolbar 标题显示对话 title（无 title 时显示 "新对话"）
- 移除 welcome message 的硬编码（历史对话不需要显示欢迎语）
  - 仅新对话第一次进入时显示欢迎语

#### 6. AndroidManifest 修改
- 注册 ConversationListActivity
- launcher fast-path 目标保持 LoginActivity（LoginActivity 自动跳转）

### 文件清单
- 新增: `ConversationListActivity.java`, `activity_conversation_list.xml`, `item_conversation.xml`
- 修改: `ClawPhonesAPI.java`, `ChatActivity.java`, `LoginActivity.java`, `AndroidManifest.xml`

### 样式规范
- 保持现有深色主题: 背景 #1A1A1A, 表面 #2A2A2A, 文字 #F5F0E6, 强调色 #E8A853
- FAB 使用强调色 #E8A853
- 列表 item 高度 72dp，左右 padding 16dp
- 空状态文字居中，颜色 #888888

### 验收标准
- [ ] 登录后进入对话列表页，显示所有历史对话
- [ ] 点击对话进入聊天，显示历史消息
- [ ] FAB 创建新对话并进入聊天
- [ ] 左滑删除对话（有确认弹窗）
- [ ] ChatActivity 返回回到列表页（列表自动刷新）
- [ ] 空状态正确显示
- [ ] 无 crash，lifecycle 正确（旋转屏幕不丢失状态）

### 注意
- BASE_URL 已在 ClawPhonesAPI.java 中定义，直接复用
- 不要改动 streaming 相关代码
- 时间格式用 SimpleDateFormat，注意 created_at 是 unix timestamp (seconds)
- executor + handler 模式保持和 ChatActivity 一致
