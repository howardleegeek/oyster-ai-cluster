## 任务: S2-4 Android Launcher 死代码清理

### 背景
ClawPhones Android 是从 BotDrop fork 的，还有残留的 BotDrop 引用和重复代码。需要清理以减少混淆和包大小。

### 具体要求
1. **BotDrop 引用清理**:
   - `AuthFragment.java` (line 45): 注释引用 `fragment_botdrop_auth_input.xml`，更新注释
   - `TermuxInstaller.java`: 3 处 `app.botdrop` 包名引用 → 改为 `ai.clawphones.agent`
   - `TermuxInstaller.java` line ~130: `OLD_PREFIX = "/data/data/app.botdrop/"` → 更新

2. **重复 ChatActivity 清理**:
   - `ai/clawphones/agent/ChatActivity.java` (411行，旧版)
   - `ai/clawphones/agent/chat/ChatActivity.java` (611行，新版)
   - 确认旧版是否被 AndroidManifest.xml 或其他代码引用，如果没有则删除

3. **死 Fragment 检查**:
   - `PlaceholderFragment.java` — 检查是否被引用，没有则删除
   - `com/termux/app/fragments/settings/` 下 5+ settings fragments — 如果 ClawPhones 没有 settings 界面引用它们，标记但不删 (Termux 可能内部用)

4. **死 import 清理**: 每个修改过的文件移除未使用的 import

### 文件
- 工作目录: `~/.openclaw/workspace/android/clawphones-android/`
- AndroidManifest: `app/src/main/AndroidManifest.xml`
- 扫描范围: `app/src/main/java/ai/clawphones/agent/`

### 验收标准
- [ ] 零 `botdrop` 或 `BotDrop` 引用 (grep -ri "botdrop" 验证)
- [ ] 旧版 ChatActivity 已删除或合并 (如果确认未使用)
- [ ] 无 unused import warnings (Android lint)
- [ ] 编译通过
- [ ] AndroidManifest.xml 中的 activity 声明与实际文件一一对应

### 注意
- Termux 相关文件要小心，它们有内部依赖关系
- 删文件前一定 grep 确认无引用
- 不要动 com.termux 包的核心逻辑，只改 BotDrop 引用字符串
