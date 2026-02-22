## 任务: S6-3 Dark Mode 开关

### 背景
双端目前跟随系统主题，没有 APP 内切换开关。

### 具体要求

#### Android
1. 在 Settings 添加 "外观" → "深色模式" 选项: 跟随系统 / 浅色 / 深色
2. 使用 `AppCompatDelegate.setDefaultNightMode()` 切换
3. 保存选择到 SharedPreferences
4. 确保所有界面在两种模式下可读 (对比度足够)

#### iOS
1. 在 SettingsView 添加 "外观" section
2. 选项: 跟随系统 / 浅色 / 深色
3. 使用 `@Environment(\.colorScheme)` + `preferredColorScheme()` 覆盖
4. 保存到 `@AppStorage`

### 文件
- Android: 改 Settings 相关文件 + themes.xml
- iOS: 改 `SettingsView.swift` + `ContentView.swift`

### 验收标准
- [ ] Settings 里有三个选项 (系统/浅/深)
- [ ] 切换立即生效
- [ ] 重启 APP 保持选择
- [ ] 所有界面在深色模式下文字可读
- [ ] 编译通过 (双端)
