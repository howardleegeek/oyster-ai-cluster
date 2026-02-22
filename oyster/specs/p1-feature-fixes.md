## 任务: 修复 P1 Feature Gaps — enum 对齐 + 依赖补全 + TODO 清理

### 背景
Sprint 2-10 验收发现 P1 级别问题：跨平台 enum 命名不一致导致 API mismatch、缺失依赖声明、代码中残留 TODO。

### 工作目录
`~/.openclaw/workspace/`

### 具体要求

---

#### P1-1: Enum 命名对齐 (tier/persona)
**问题**: 后端、iOS、Android 对 tier 和 persona 的枚举值命名不一致
**要求**:
1. 在 `proxy/server.py` 中找到 tier 和 persona 的枚举定义
2. 在 iOS 代码中找到对应的 enum（Swift enum 或 string constants）
3. 在 Android 代码中找到对应的 enum（Java enum 或 string constants）
4. 以**后端定义为准**，统一三端命名
5. 确保 JSON 序列化/反序列化使用相同的 string 值

---

#### P1-2: 依赖声明补全
**要求**:
1. 检查 `proxy/requirements.txt`（或 pyproject.toml）—— 确保所有 import 的包都在依赖列表中
2. 检查 `ios/ClawPhones/` 的 Package.swift 或 Podfile —— 确保所有 import 的框架都声明
3. 检查 `android/.../build.gradle` —— 确保所有 import 的库都在 dependencies 中
4. 特别注意: EncryptedSharedPreferences (P0-6 会添加)、H3 库、推送通知库

---

#### P1-3: TODO 清理
**要求**:
1. `grep -rn "TODO\|FIXME\|HACK\|XXX"` 在整个 workspace
2. 对每个 TODO:
   - 如果是已完成的功能 → 删除 TODO 注释
   - 如果是有意义的待办 → 保留但添加 issue 编号
   - 如果是过时的 → 删除
3. 报告最终剩余的 TODO 数量

---

### 验收标准
- [ ] 三端 tier enum 值完全一致（后端为准）
- [ ] 三端 persona enum 值完全一致（后端为准）
- [ ] 所有 import 的包都在依赖声明中
- [ ] TODO 数量从 9 减少到 ≤3（仅保留真正待办的）
- [ ] 编译通过（Python + iOS + Android）

### 注意
- enum 修改可能影响已有数据 —— 如果后端 DB 中已存储旧 enum 值，需要兼容处理
- 不改 API 行为，只对齐命名
