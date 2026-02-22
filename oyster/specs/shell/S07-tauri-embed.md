---
task_id: S07-tauri-embed
project: shell-vibe-ide
priority: 2
estimated_minutes: 30
depends_on: ["S01-fork-bolt-diy", "S02-cyberpunk-theme"]
modifies: ["desktop/src-tauri/tauri.conf.json", "desktop/src/App.tsx", "desktop/package.json"]
executor: glm
---

## 目标

让现有 Tauri Desktop 壳加载 bolt.diy fork (web-ui/) 的 UI，而不是原来简单的 App.tsx。

## 步骤

1. 修改 `desktop/tauri.conf.json`:
   - `devPath` 改为指向 web-ui 的 dev server (如 `http://localhost:5173`)
   - 或者让 desktop 的 vite 代理到 web-ui
2. 修改 `desktop/src/App.tsx`:
   - 方案 A (推荐): 直接 iframe 嵌入 web-ui
   - 方案 B: 将 web-ui 的入口组件导入 desktop 的 React app
   - 方案 C: 让 Tauri 直接加载 web-ui 的构建产物
3. 更新 `desktop/package.json`:
   - 添加 workspace 引用或 dev script 同时启动 web-ui 和 tauri
4. 创建 `desktop/start.sh` (或更新现有的):
   ```bash
   # 同时启动 web-ui dev server 和 Tauri
   cd ../web-ui && pnpm dev &
   cd ../desktop && cargo tauri dev
   ```
5. 更新窗口标题: "Shell - Web3 Vibe Coding IDE"

## 方案推荐

**方案 C 最干净**: 让 Tauri 的 `devPath` 直接指向 web-ui 的 dev server。生产构建时，先 build web-ui，然后 Tauri 加载构建产物。这样 Desktop 和 Web 用完全相同的代码。

```json
// tauri.conf.json
{
  "build": {
    "devPath": "http://localhost:5173",
    "distDir": "../web-ui/dist",
    "beforeDevCommand": "cd ../web-ui && pnpm dev",
    "beforeBuildCommand": "cd ../web-ui && pnpm build"
  }
}
```

## 约束

- 保留现有 `commands.rs` (Rust 后端能力)
- 不要删除 Tauri 的 Rust 后端代码
- 确保 Tauri invoke 仍然可用 (web-ui 中可以调用 Tauri 命令)
- 窗口大小保持 1200x800 最小 800x600

## 验收标准

- [ ] `cargo tauri dev` 启动后显示 bolt.diy UI (带赛博朋克主题)
- [ ] 窗口标题为 "Shell - Web3 Vibe Coding IDE"
- [ ] Tauri invoke 功能正常 (可调用 run_web3_command)
- [ ] 窗口可调整大小，最小 800x600
- [ ] 退出时进程正确清理

## 不要做

- 不要改 commands.rs
- 不要改 Rust 后端逻辑
- 不要实现新的 Tauri commands
- 不要改 web-ui 的功能代码
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
