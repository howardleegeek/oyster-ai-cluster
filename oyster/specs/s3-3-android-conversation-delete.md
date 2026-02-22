## 任务: S3-3 Android 会话删除

### 背景
iOS 有 swipe-to-delete 会话功能，Android 的 ConversationListActivity 还没有实现删除。

### 具体要求
1. 在 `ConversationListActivity` 添加长按或滑动删除手势
2. 弹出确认对话框 "确定删除此会话？"
3. 调用 `DELETE /v1/conversations/{id}`
4. 删除成功后从列表移除，动画过渡
5. 删除失败显示 Toast 错误

### 参考
- iOS 实现: `ConversationListView.swift` (swipe action)
- API: `ConversationApiClient.java` 检查是否已有 delete 方法

### 文件
- 工作目录: `~/.openclaw/workspace/android/clawphones-android/`
- 主文件: ConversationList 相关的 Activity/Adapter

### 验收标准
- [ ] 长按会话 → 确认弹窗 → 删除
- [ ] 删除后列表立即更新 (不需要手动刷新)
- [ ] 网络错误时显示错误提示
- [ ] 编译通过
