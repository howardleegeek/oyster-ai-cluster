## 任务: Android 对话历史 + 加载态 + Logout (合并 S1-1 + S1-2)

### 背景
当前 Android ChatActivity 每次启动都创建新对话，用户无法查看/恢复历史。同时缺少加载态、思考指示器和 logout。
ClawPhonesAPI.java 已经有 getConversations / deleteConversation / getMessages 方法（刚加的），直接用。

### 后端 API（已存在）
```
GET    /v1/conversations              → [{id, title, created_at, updated_at, message_count}, ...]
POST   /v1/conversations              → {id, title, created_at}
DELETE /v1/conversations/{id}         → 204
GET    /v1/conversations/{id}/messages → [{id, role, content, created_at}, ...]
```
Header: `Authorization: Bearer <token>`
BASE_URL 已定义在 ClawPhonesAPI.java。

---

### Part A: ConversationListActivity (新增)

#### 新增文件
1. `app/src/main/java/ai/clawphones/agent/chat/ConversationListActivity.java`
2. `app/src/main/res/layout/activity_conversation_list.xml`
3. `app/src/main/res/layout/item_conversation.xml`

#### activity_conversation_list.xml 布局
```xml
- 根布局: CoordinatorLayout (背景 #1A1A1A)
- Toolbar: 标题 "ClawPhones"，右侧 logout 图标 (ImageButton, ic_logout 或文字 "退出")
- RecyclerView: id=conversations_recycler, 填满中间
- FloatingActionButton: 右下角, 背景 #E8A853, "+" 图标
- 空状态: id=empty_state, 居中 "暂无对话\n点击 + 开始聊天" (颜色 #888888, 默认 GONE)
```

#### ConversationListActivity.java 逻辑
```
onCreate:
  1. 检查 token (SharedPreferences "clawphones_token")，无 token → LoginActivity
  2. 初始化 RecyclerView + Adapter + FAB
  3. loadConversations()

loadConversations():
  - ExecutorService 后台调 ClawPhonesAPI.getConversations(token)
  - 成功: 更新 adapter data, 空列表显示 empty_state
  - 失败 (401): 清 token → LoginActivity
  - 失败 (其他): Toast "加载失败"

Adapter (ConversationAdapter, 内部类):
  - 每行: title (无标题→"新对话"), message_count badge, 相对时间
  - 相对时间: "刚刚"/<5min "X分钟前"/<1h "X小时前"/昨天/日期
  - click → ChatActivity (传 conversation_id + title extra)

左滑删除:
  - ItemTouchHelper.SimpleCallback, swipeDir=LEFT
  - 弹 AlertDialog "确定删除这个对话吗？"
  - 确认 → ClawPhonesAPI.deleteConversation() → 移除 item

FAB click:
  - 直接启动 ChatActivity (不传 conversation_id)

Logout (toolbar 按钮):
  - AlertDialog "确定退出登录吗？"
  - 确认 → 清 SharedPreferences token
  - Intent(LoginActivity) + FLAG_ACTIVITY_NEW_TASK | FLAG_ACTIVITY_CLEAR_TASK

onResume:
  - 每次返回列表都 loadConversations() (刷新列表)
```

#### item_conversation.xml
```xml
- 高度 72dp, padding 16dp
- 左侧: title (TextView, 16sp, #F5F0E6, 单行 ellipsize end)
- 右上: 相对时间 (TextView, 12sp, #888888)
- 左下: message_count + "条消息" (TextView, 12sp, #888888)
- 背景: #2A2A2A, 圆角 8dp, marginBottom 4dp
```

---

### Part B: ChatActivity 修改

#### 接收对话历史
```
onCreate:
  - 读 intent extra "conversation_id"
  - 有值: mConversationId = extra, 调 loadHistory()
  - 无值: 创建新对话 (保持现有逻辑), 显示欢迎语

loadHistory(conversationId):
  - 后台调 ClawPhonesAPI.getMessages(token, conversationId)
  - 成功: 按时间顺序添加到 mMessages list, 刷新 adapter, 滚动到底部
  - 失败: Toast "加载历史失败"
```

#### Toolbar 改进
- 标题: 有 intent extra "title" → 显示它; 否则 "新对话"
- 添加 back button (toolbar.setNavigationOnClickListener → finish())
- 右侧 overflow menu (3 dots):
  - "退出登录" → 同 ConversationListActivity 的 logout 逻辑

#### 思考中指示器
```
onSend() 中:
  1. 添加 user message 到列表
  2. 添加一条 assistant message, content = "思考中..."
     (这条消息的 index 记为 thinkingIdx)
  3. 开始 streaming
  4. onDelta 第一次触发: 用 accumulated content 替换 "思考中..."
```

#### 发送按钮加载态
- 发送后: send button 替换为小 ProgressBar (或 setEnabled(false) + alpha 0.5)
- onComplete / onError: 恢复 send button

#### 错误重试
```
保存 mLastUserText (每次 onSend 时记录)

onError:
  - 如果 accumulated 有内容: 显示 accumulated + "\n\n⚠️ 连接中断"
  - 如果 accumulated 为空: 显示 "⚠️ 发送失败"
  - mBusy = false, 恢复输入
  (用户可以直接重新发送消息)
```

---

### Part C: LoginActivity 修改

#### 登录成功跳转改为 ConversationListActivity
```java
// 原来: startActivity(new Intent(this, ChatActivity.class))
// 改为:
startActivity(new Intent(this, ConversationListActivity.class));
finish();
```

#### 登录加载态
```
点击登录/注册后:
  - mSubmitBtn.setEnabled(false)
  - mSubmitBtn.setText("登录中...") 或 "注册中..."
  - 禁用输入框

成功/失败后:
  - 恢复按钮文字和 enabled 状态
```

---

### Part D: AndroidManifest.xml

添加:
```xml
<activity android:name=".chat.ConversationListActivity"
    android:theme="@style/Theme.AppCompat.NoActionBar"
    android:screenOrientation="portrait" />
```

---

### 样式规范
- 背景: #1A1A1A, 表面: #2A2A2A, 文字: #F5F0E6, 次要文字: #888888
- 强调色: #E8A853 (FAB, 按钮)
- 用户 bubble: #2F80ED, AI bubble: #3A3A2E
- item 圆角 8dp, FAB 圆角默认
- "思考中..." 文字: italic, #888888

### 验收标准
- [ ] 登录后进入 ConversationListActivity
- [ ] 列表显示所有历史对话 (title + 消息数 + 相对时间)
- [ ] 点击对话 → ChatActivity 显示历史消息
- [ ] FAB 创建新对话进入空聊天
- [ ] 左滑删除有确认弹窗
- [ ] 空状态正确显示
- [ ] ChatActivity 有 back button 回到列表
- [ ] "思考中..." 在 AI 回复前显示，streaming 开始后替换
- [ ] 登录按钮有 loading 态
- [ ] 发送失败显示错误提示
- [ ] Logout 在两个页面都可用
- [ ] 全流程 gradlew assembleDebug 编译通过
- [ ] 无 crash

### 注意
- ClawPhonesAPI.java 已有 getConversations/deleteConversation/getMessages 三个方法，检查一下能不能直接用，不能用就修复
- executor + handler 模式和现有代码保持一致
- 不要改 streaming 核心逻辑
- created_at / updated_at 是 unix timestamp (seconds, 不是 milliseconds)
- build 命令: JAVA_HOME=/opt/homebrew/Cellar/openjdk@17/17.0.18/libexec/openjdk.jdk/Contents/Home ./gradlew assembleDebug
