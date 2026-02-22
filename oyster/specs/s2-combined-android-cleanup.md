## 任务: Android 字符串外部化 + Launcher 死代码清理 (S2-1 + S2-4)

### Part A: 字符串外部化 (S2-1)

把所有 ClawPhones 相关的硬编码中文字符串移到 res/values/strings.xml。

#### 需要提取的字符串 (搜索以下文件):
- `ConversationListActivity.java`: "暂无对话", "确定删除这个对话吗？", "确定退出登录吗？", "新对话", "条消息", "加载失败", "刚刚", "分钟前", "小时前", "昨天"
- `ChatActivity.java`: "你好！有什么我可以帮你的吗？", "思考中...", "⚠️ 连接中断", "⚠️ 发送失败", "加载历史失败", "登录已过期，请重新登录", "新对话", "确定退出登录吗？"
- `LoginActivity.java`: "登录中...", "注册中...", "登录", "注册", "未知错误"
- Layout XML files: "输入消息…", "暂无对话\n点击 + 开始聊天", "退出登录", "新建对话"

#### 做法:
1. 在 `app/src/main/res/values/strings.xml` 中添加所有字符串 (保留现有 Termux 字符串不动)
2. 在 Java 代码中用 `getString(R.string.xxx)` 或 `getResources().getString(R.string.xxx)` 替换
3. 在 XML 中用 `@string/xxx` 替换
4. 命名规范: `clawphones_` 前缀, snake_case, 例如 `clawphones_thinking`, `clawphones_login_button`

### Part B: Launcher 死代码清理 (S2-4)

文件: `ClawPhonesLauncherActivity.java`

#### 做法:
1. 删除 Phase 1 welcome container 相关的所有代码 (权限请求 UI)
2. 删除 Phase 2 loading 相关的死代码
3. 只保留 fast-path: 检查 token → 有就跳 ConversationListActivity，没有跳 LoginActivity
4. 删除不再使用的 import
5. 最终文件应该 < 30 行有效代码

### 验收标准
- [ ] 所有中文硬编码字符串都在 strings.xml 中
- [ ] Java 代码中没有中文字符串 (除了注释)
- [ ] XML layout 中没有硬编码中文文字
- [ ] ClawPhonesLauncherActivity.java 只有 fast-path 逻辑
- [ ] gradlew assembleDebug 编译通过
- [ ] build 命令: JAVA_HOME=/opt/homebrew/Cellar/openjdk@17/17.0.18/libexec/openjdk.jdk/Contents/Home ./gradlew assembleDebug
