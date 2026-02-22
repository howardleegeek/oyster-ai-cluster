---
task_id: S09-local-chains
project: shell-vibe-ide
priority: 1
estimated_minutes: 40
depends_on: ["S06-chain-selector"]
modifies: ["web-ui/app/**/*.tsx", "desktop/src-tauri/src/commands.rs"]
executor: glm
---

## 目标

在 IDE 中集成本地链管理：一键启动/停止 Solana test-validator (SVM) 或 Anvil (EVM)。

## 步骤

1. 在状态栏或侧边栏加入 "Local Chain" 面板:
   - 显示: 链类型 + 运行状态 (Running/Stopped) + RPC URL
   - 按钮: Start / Stop
2. SVM 模式:
   - 启动: `solana-test-validator` (后台进程)
   - RPC: `http://localhost:8899`
   - 状态检测: `solana cluster-version --url localhost`
3. EVM 模式:
   - 启动: `anvil` (后台进程)
   - RPC: `http://localhost:8545`
   - 状态检测: 查看进程是否存活
4. Desktop: 通过 Tauri command 管理进程 (复用 commands.rs 的进程管理)
5. Web App: 通过 API endpoint 管理 (需要后端)
6. 显示预置账户/余额 (Anvil 提供 10 个测试账户)

## UI 设计

```
┌─ Local Chain ──────────────────┐
│  ● SVM (Solana Test Validator) │
│  Status: Running               │
│  RPC: http://localhost:8899    │
│  [Stop]                        │
└────────────────────────────────┘
```

## 验收标准

- [ ] 一键启动 solana-test-validator
- [ ] 一键启动 anvil
- [ ] 状态栏显示链运行状态
- [ ] 停止按钮正常关闭进程
- [ ] RPC URL 显示在 UI 中
- [ ] 退出 IDE 时自动清理进程

## 不要做

- 不要实现主网连接
- 不要实现钱包 (S11 做)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
