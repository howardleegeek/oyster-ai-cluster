## 任务: S8-2 对话数据导出

### 背景
GDPR 合规 + 用户信任，需要支持导出个人数据。

### 具体要求

#### 后端
1. 新增 `GET /v1/user/export` — 导出用户所有数据
2. 返回 JSON: 用户 profile + 所有会话 + 所有消息
3. 异步生成 (大数据量时)，返回下载链接

#### 双端
1. Settings 添加 "导出我的数据" 按钮
2. 点击后调用 API → 下载 JSON 文件
3. 使用系统分享/保存文件对话框

### 文件
- 后端: `server.py`
- iOS: `SettingsView.swift`
- Android: Settings 相关

### 验收标准
- [ ] 导出包含完整用户数据 (profile + conversations + messages)
- [ ] 文件可通过系统分享/保存
- [ ] 大数据量不超时 (异步处理)
- [ ] 编译通过 (双端)
