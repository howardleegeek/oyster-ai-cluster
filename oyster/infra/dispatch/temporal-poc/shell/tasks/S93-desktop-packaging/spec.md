## 目标

打包 Shell Desktop App (Tauri) 为 macOS dmg，建立自动化发布流水线。

## 步骤

1. **完善 `desktop/tauri.conf.json`**:
   - 设置正确的 app identifier: `com.oyster.shell`
   - 配置 window 大小、标题
   - 设置 icon (使用现有 logo)
   - 配置 bundle targets: `["dmg", "app"]`

2. **更新 `desktop/src-tauri/`**:
   - `Cargo.toml` — 确认依赖版本
   - `src/main.rs` — 添加 Tauri commands:
     - `start_opencode_server` — 启动 opencode serve
     - `get_shell_status` — 获取 shell-run 状态
     - `read_report` — 读取报告 JSON

3. **创建 `.github/workflows/release.yml`**:
   ```yaml
   name: Release Desktop App
   on:
     push:
       tags: ['v*']
   jobs:
     build-macos:
       runs-on: macos-latest
       steps:
         - uses: actions/checkout@v4
         - uses: dtolnay/rust-toolchain@stable
         - uses: actions/setup-node@v4
         - run: cd desktop && pnpm install
         - run: cd desktop && pnpm tauri build
         - uses: softprops/action-gh-release@v2
           with:
             files: desktop/src-tauri/target/release/bundle/dmg/*.dmg
   ```

4. **验证本地构建**:
   - `cd desktop && pnpm install && pnpm tauri build`

## 约束

- 只打包 macOS (Linux/Windows 后续)
- 不要自签名 (开发者 ID 签名后续配置)
- Tauri v2 API
- 最小权限: 只需要文件系统和网络

## 验收标准

- [ ] `tauri.conf.json` 配置完整
- [ ] Tauri commands 编译通过
- [ ] GitHub Actions workflow 语法正确
- [ ] 本地 `pnpm tauri build` 成功生成 .app

## 不要做

- 不要添加 auto-update 功能
- 不要配置代码签名
- 不要修改 web-ui 代码