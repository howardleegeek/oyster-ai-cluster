## 任务: S8-3 账号删除

### 背景
App Store 和 GDPR 要求支持账号删除。

### 具体要求

#### 后端
1. 新增 `DELETE /v1/user/account` 端点
2. 需要密码确认 (body: {"password": "..."})
3. 删除: 用户数据 + 所有会话 + 所有消息 + push tokens + crash reports
4. 保留 usage 统计 (匿名化)
5. 返回确认，使 token 失效

#### 双端
1. Settings 最底部添加红色 "删除账号" 按钮
2. 二次确认弹窗: "此操作不可撤销，将删除所有数据"
3. 输入密码确认
4. 删除成功 → 清除本地数据 → 返回登录页

### 文件
- 后端: `server.py`
- iOS: `SettingsView.swift`, `AuthViewModel.swift`
- Android: Settings + auth 相关

### 验收标准
- [ ] 需要密码确认才能删除
- [ ] 二次确认弹窗
- [ ] 后端数据完全删除 (除匿名统计)
- [ ] 本地数据清除
- [ ] 删除后返回登录页
- [ ] 编译通过 (双端)
