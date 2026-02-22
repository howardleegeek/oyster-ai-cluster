## 任务: Android 加载态 + 思考指示器 + 错误恢复 + Logout

### 背景
当前 Android 聊天缺少视觉反馈：登录时无 spinner、发消息时无 "思考中" 指示、出错后无 retry。同时缺少 logout 功能。

### 具体要求

#### 1. LoginActivity 加载态
- 点击登录/注册后:
  - 按钮文字改为 "登录中..." / "注册中..."
  - 按钮旁显示小 ProgressBar (indeterminate, 20dp, 白色)
  - 禁用所有输入框和按钮
- 成功/失败后恢复原状

#### 2. ChatActivity "思考中" 指示器
- 用户发送消息后，在 AI 回复 bubble 位置显示 "思考中..." 动画:
  - 3 个圆点，依次闪烁 (alpha 动画, 500ms 循环)
  - 或者简单实现: 文字 "思考中..." 用 italic 灰色显示
- 第一个 streaming delta 到达后，替换为实际内容
- 实现方式: 在 onSend() 里添加一条 role=assistant, content="思考中..." 的临时消息，onDelta 首次触发时替换

#### 3. 网络错误 retry
- streaming 失败时（onError 回调）:
  - 在 AI 回复 bubble 显示: "[已收到的部分内容]\n\n⚠️ 连接中断"
  - bubble 下方显示一个 "重试" 按钮 (小按钮，强调色)
  - 点击 "重试": 重新发送用户的最后一条消息
- 实现: 在 ChatAdapter 的 assistant bubble 布局中添加一个 retry_button (默认 GONE)
  - 当消息内容包含 "⚠" 时显示 retry 按钮
  - 点击 retry 回调到 ChatActivity

#### 4. Logout 功能
- ChatActivity toolbar 右侧添加 overflow menu (3 dots)
  - 菜单项: "退出登录"
- ConversationListActivity toolbar 右侧添加同样的 logout 图标
- 点击 logout:
  - AlertDialog 确认: "确定退出登录吗？"
  - 确认后: 清除 SharedPreferences 中的 token，跳转 LoginActivity，清除 back stack
  - `intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK)`

### 文件清单
- 修改: `LoginActivity.java`, `ChatActivity.java`, `activity_login.xml`
- 修改: `ChatAdapter` (如果是内部类则在 ChatActivity.java 内)
- 新增: `res/menu/chat_menu.xml` (overflow menu)

### 样式规范
- ProgressBar: 小型 indeterminate, 白色 tint
- "思考中..." 文字: italic, 颜色 #888888
- Retry 按钮: 小型, 背景 #E8A853, 文字 "重试", 圆角 8dp
- Logout 图标: 使用 Android 内置 ic_menu_close_clear_cancel 或简单用文字

### 验收标准
- [ ] 登录时按钮显示 spinner，输入框禁用
- [ ] 发消息后立即看到 "思考中..." bubble
- [ ] streaming 开始后 "思考中..." 被替换为实际内容
- [ ] 网络断开时显示部分内容 + 重试按钮
- [ ] 点击重试能重新发送最后一条消息
- [ ] Logout 弹确认框，确认后清 token 回到登录页
- [ ] 全流程无 crash

### 注意
- "思考中" 的实现尽量简单，不需要复杂动画，灰色 italic 文字即可
- retry 按钮的核心是保存最后发送的 userText，失败时用它重发
- 这个任务依赖 S1-1（ConversationListActivity），如果 S1-1 还没完成，logout 先只在 ChatActivity 实现
