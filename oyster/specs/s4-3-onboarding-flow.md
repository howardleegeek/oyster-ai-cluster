## 任务: S4-3 新用户 Onboarding 流程

### 背景
用户首次打开 APP 直接进入登录页，没有产品介绍。需要引导流程。

### 具体要求

#### 双端通用设计
1. 3-4 个欢迎页面 (swipe/滑动切换):
   - 页面 1: "AI Assistant" — 介绍 ClawPhones 是什么
   - 页面 2: "Multiple AI Models" — DeepSeek/Kimi/Claude 多模型
   - 页面 3: "Your Data, Your Device" — 隐私和本地运行
   - 页面 4: "Get Started" → 跳转注册/登录
2. 底部小圆点指示器 + Skip 按钮
3. 首次安装才显示，之后不再出现 (SharedPreferences/UserDefaults 标记)

#### Android
1. 新建 `OnboardingActivity.java` + ViewPager2
2. 在 `ClawPhonesLauncherActivity` 中检查是否首次启动
3. 首次 → OnboardingActivity，之后 → LoginActivity

#### iOS
1. 新建 `OnboardingView.swift` + TabView with PageTabViewStyle
2. 在 `ContentView.swift` 中检查 `@AppStorage("hasSeenOnboarding")`
3. 首次 → OnboardingView，之后 → LoginView/ConversationListView

### 文件
- Android: 新建 `OnboardingActivity.java` + layout XMLs, 改 `ClawPhonesLauncherActivity.java`
- iOS: 新建 `OnboardingView.swift`, 改 `ContentView.swift`

### 验收标准
- [ ] 首次安装显示 Onboarding (3-4 页)
- [ ] 可滑动切换 + Skip 跳过
- [ ] 完成后进入登录/注册
- [ ] 第二次打开不再显示
- [ ] 编译通过 (双端)
