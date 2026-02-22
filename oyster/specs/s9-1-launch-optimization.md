## 任务: S9-1 启动速度优化

### 背景
APP 启动慢影响用户体验，需要优化冷启动时间。

### 具体要求

#### Android
1. 测量当前冷启动时间 (adb shell am start -W)
2. 实现 SplashScreen API (Android 12+)
3. 延迟初始化非必要组件 (Crash reporter 可延迟、网络监听可延迟)
4. 移除 Application.onCreate() 中的阻塞操作
5. 目标: 冷启动 < 1.5 秒

#### iOS
1. 测量当前启动时间 (Instruments)
2. `ClawPhonesApp.init` 中延迟非必要初始化
3. 用 `task {}` 异步初始化网络层和缓存
4. 目标: 冷启动 < 1 秒

### 文件
- Android: `ClawPhonesApplication.java` (如果有) 或 launcher activity
- iOS: `ClawPhonesApp.swift`

### 验收标准
- [ ] 启动时间有可测量的改善
- [ ] SplashScreen 正确显示品牌 logo
- [ ] 延迟初始化不影响功能
- [ ] 编译通过 (双端)
