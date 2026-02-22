---
task_id: S68-live-reload
project: shell-vibe-ide
priority: 2
estimated_minutes: 20
depends_on: ["S05-build-integration", "S09-local-chains"]
modifies: ["web-ui/app/lib/stores/livereload.ts", "web-ui/app/components/workbench/LiveReloadToggle.tsx"]
executor: glm
---

## 目标

Live Reload 开发模式：文件保存后自动重新编译部署到本地链，实现合约热更新开发体验。

## 步骤

1. `web-ui/app/lib/stores/livereload.ts`:
   - nanostores atom: `liveReloadEnabled` (boolean, 默认 false)
   - `liveReloadStatus` (idle/compiling/deploying/ready/error)
   - `lastDeployAddress` — 最近部署的合约地址
   - 文件监听: 使用 bolt.diy 已有的文件变更检测
   - 流程: file change → debounce 1s → compile → deploy to local chain → 更新地址
2. `web-ui/app/components/workbench/LiveReloadToggle.tsx`:
   - 开关按钮 (在编辑器工具栏)
   - 状态指示: 绿点=ready, 黄点=compiling, 红点=error
   - 前置条件检查:
     - 本地链必须在运行 (S09)
     - 编译器必须可用 (S05/S15)
   - 每次 deploy 后在终端显示新地址
3. 安全:
   - 只在本地链 (Anvil/test-validator) 上启用
   - testnet/mainnet 禁止 live reload

## 验收标准

- [ ] 文件保存自动编译
- [ ] 自动部署到本地链
- [ ] 状态指示正确
- [ ] 非本地链时禁用

## 不要做

- 不要实现前端 HMR (只做合约)
- 不要在测试网/主网启用
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
