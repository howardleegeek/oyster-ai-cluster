## 任务: S8-1 生物识别锁

### 背景
保护隐私，APP 打开时可要求 Face ID / 指纹验证。

### 具体要求

#### iOS
1. Settings 添加 "Face ID / Touch ID 锁定" 开关
2. 启用后，APP 从后台回来时要求生物识别
3. 使用 `LocalAuthentication` framework (`LAContext`)
4. 验证失败 → 不允许进入，显示 "请验证身份"
5. 3 次失败 → fallback 到密码

#### Android
1. Settings 添加 "指纹/面部解锁" 开关
2. 使用 `BiometricPrompt` API
3. 同样的进入保护逻辑

### 文件
- iOS: `SettingsView.swift`, `ContentView.swift`
- Android: Settings + `ClawPhonesLauncherActivity.java`

### 验收标准
- [ ] Settings 有生物识别开关
- [ ] 开启后从后台返回需要验证
- [ ] 验证成功正常进入
- [ ] 验证失败阻止访问
- [ ] 设备不支持生物识别时隐藏该选项
- [ ] 编译通过 (双端)
