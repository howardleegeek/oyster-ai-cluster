## 任务: S2-1 Android 字符串外部化

### 背景
ClawPhones Android 端有 ~80-120 个硬编码中文字符串散落在 Java 文件中，需要提取到 strings.xml 以支持未来国际化。strings.xml 已存在 (650行，Termux 部分已外部化)。

### 具体要求
1. 扫描 `ai.clawphones.agent` 包下所有 Java 文件，找出硬编码字符串
2. 重点文件:
   - `chat/LoginActivity.java` — 注册/登录/已有账号等 ~20 个字符串
   - `chat/ChatActivity.java` (611行) — 新对话/退出登录等 UI 标签
   - `ChatActivity.java` (411行，旧版) — 同上
   - `DashboardActivity.java`, `PreinstallActivity.java`
3. 提取到 `app/src/main/res/values/strings.xml`，命名规范: `snake_case`，分 section 注释
4. Java 代码中替换为 `getString(R.string.xxx)` 或 XML 中 `@string/xxx`
5. 不动 `com.termux` 包下的文件

### 文件
- 工作目录: `~/.openclaw/workspace/android/clawphones-android/`
- 主文件: `app/src/main/res/values/strings.xml`
- 扫描范围: `app/src/main/java/ai/clawphones/agent/**/*.java`

### 验收标准
- [ ] `ai.clawphones.agent` 包下无硬编码中文字符串 (grep 验证)
- [ ] strings.xml 新增条目有清晰注释分组
- [ ] 编译通过 (`./gradlew assembleDebug` 或至少无语法错误)
- [ ] 不改动 Termux 相关代码

### 注意
- Toast 消息也要外部化
- Dialog 标题和按钮文字也要
- Log 消息保留英文，不需要外部化
