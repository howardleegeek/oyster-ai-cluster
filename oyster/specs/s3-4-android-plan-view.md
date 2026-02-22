## 任务: S3-4 Android Plan 界面

### 背景
iOS 有 PlanView 展示 tier 对比和当前用量，Android 缺少这个界面。

### 具体要求
1. 新建 `PlanActivity.java` 或在 Settings 里加一个 Plan section
2. 调用 `GET /v1/user/plan` 获取:
   - 当前 tier (free/pro/max)
   - 今日 token 用量 vs 上限
   - 各 tier 功能对比
3. 显示进度条: 今日用量 / 每日上限
4. 各 tier 对比卡片 (context length, output limit, daily cap)
5. 从 Settings 页面可导航到 Plan 页面

### 参考
- iOS 实现: `PlanView.swift`
- 后端: `GET /v1/user/plan` 返回格式

### 文件
- 工作目录: `~/.openclaw/workspace/android/clawphones-android/`
- 新建或修改: Plan 相关 Activity + layout XML

### 验收标准
- [ ] Plan 界面显示当前 tier + 用量进度条
- [ ] 三个 tier 的功能对比表
- [ ] Settings → Plan 导航正常
- [ ] 编译通过
