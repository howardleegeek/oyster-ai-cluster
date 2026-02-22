## 任务: S10-3 Release Build 配置

### 背景
确保双端能正确打包 Release 版本。

### 具体要求

#### Android
1. 配置 ProGuard/R8 规则 (保留必要类)
2. 配置签名 (release keystore)
3. `./gradlew assembleRelease` 成功
4. APK 大小检查 (目标 < 30MB)
5. 移除所有 debug 日志 (Log.d/Log.v)

#### iOS
1. 配置 Release scheme
2. Archive 成功
3. 确认 code signing 配置
4. 移除 debug print 语句
5. 确认 deployment target (iOS 16.0+)

### 文件
- Android: `build.gradle`, `proguard-rules.pro`
- iOS: Xcode project settings

### 验收标准
- [ ] Android `assembleRelease` 成功
- [ ] iOS Archive 成功
- [ ] 无 debug 日志泄漏
- [ ] APK < 30MB, IPA 合理大小
- [ ] 编译通过 (双端 Release)
