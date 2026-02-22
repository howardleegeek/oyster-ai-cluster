## 任务: S10-1 App Store 发布准备

### 背景
准备 iOS App Store 和 Google Play Store 发布所需的元数据和配置。

### 具体要求

#### iOS (App Store Connect)
1. 准备 App 描述 (中文 + 英文)
2. 准备截图: iPhone 6.7" (1290×2796) — 至少 3 张
3. 设置 Privacy Policy URL 和 Terms URL
4. 配置 App 分类: Utilities / Productivity
5. 在 Info.plist 确认所有权限描述清晰
6. 确认 Bundle ID: `ai.clawphones.app`
7. 版本号: 1.0.0 (build 1)

#### Android (Google Play Console)
1. 准备 Feature Graphic (1024×500)
2. 准备 Phone Screenshots (至少 4 张)
3. 准备 App 描述 (中文 + 英文, 短描述 80字 + 长描述 4000字)
4. Content Rating questionnaire
5. 确认 applicationId: `ai.clawphones.agent`
6. 版本: versionCode 1, versionName "1.0.0"

#### 通用
1. 准备 Privacy Policy 页面 (static HTML)
2. 准备 Terms of Service 页面
3. 准备 Support URL / 联系邮箱

### 文件
- iOS: Info.plist, project settings
- Android: build.gradle, AndroidManifest.xml
- 新建: `docs/privacy-policy.html`, `docs/terms.html`

### 验收标准
- [ ] 双端版本号正确配置
- [ ] 权限描述清晰 (不会被审核拒绝)
- [ ] Privacy Policy 和 Terms 页面可访问
- [ ] 截图文案准备就绪
- [ ] 编译通过 (双端, Release build)
