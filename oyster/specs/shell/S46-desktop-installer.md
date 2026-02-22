---
task_id: S46-desktop-installer
project: shell-vibe-ide
priority: 2
estimated_minutes: 35
depends_on: ["S07-tauri-embed"]
modifies: ["desktop/src-tauri/tauri.conf.json", "desktop/src-tauri/Cargo.toml"]
executor: glm
---

## 目标

创建 Desktop App 的安装包：macOS (.dmg), Windows (.msi), Linux (.AppImage)。

## 开源方案

- **Tauri Bundler**: Tauri 内置打包工具
- **GitHub Actions**: CI/CD 自动构建

## 步骤

1. Tauri 打包配置:
   - 更新 `tauri.conf.json`:
     - identifier: `com.shell.vibe-ide`
     - copyright: "Oyster Labs"
     - category: "DeveloperTool"
     - icon: 自定义图标 (赛博朋克风)
   - macOS: .dmg + .app
   - Windows: .msi + .exe
   - Linux: .AppImage + .deb
2. GitHub Actions 自动构建:
   - 在 push to main 时触发
   - macOS (Intel + Apple Silicon)
   - Windows x64
   - Linux x64
   - 上传到 GitHub Releases
3. 自动更新:
   - Tauri updater plugin
   - 检查 GitHub Releases 最新版本
   - 通知用户更新
4. 首次运行向导:
   - 检查依赖: Node.js, Rust, Foundry, Anchor, Solana CLI
   - 缺少的自动安装或提示安装
   - 链选择 (SVM/EVM)

## 验收标准

- [ ] macOS .dmg 构建成功
- [ ] Windows .msi 构建成功
- [ ] Linux .AppImage 构建成功
- [ ] GitHub Actions CI 自动构建
- [ ] 自动更新检查
- [ ] 首次运行向导

## 不要做

- 不要签名证书 (先不做 notarization)
- 不要实现 auto-update 后台下载 (先只通知)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
