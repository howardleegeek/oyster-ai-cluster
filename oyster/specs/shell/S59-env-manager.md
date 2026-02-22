---
task_id: S59-env-manager
project: shell-vibe-ide
priority: 2
estimated_minutes: 20
depends_on: ["S06-chain-selector"]
modifies: ["web-ui/app/components/workbench/EnvManager.tsx", "web-ui/app/lib/stores/env.ts"]
executor: glm
---

## 目标

环境变量管理器：按网络管理 .env 文件，自动切换 RPC_URL、PRIVATE_KEY 等配置。

## 步骤

1. `web-ui/app/lib/stores/env.ts`:
   - nanostores atom: `envProfiles` — Map<network, Record<string, string>>
   - `activeProfile` — 当前激活的网络 profile
   - 监听 chainType/network 变化 → 自动切换 profile
2. `web-ui/app/components/workbench/EnvManager.tsx`:
   - 左侧: 网络列表 (devnet, testnet, mainnet, anvil, sepolia...)
   - 右侧: 该网络的环境变量 key-value 编辑器
   - 支持: 添加/删除/编辑变量
   - 敏感值遮掩 (点击显示)
   - "Export .env" 按钮 → 导出当前 profile 为 .env 文件
   - "Import .env" → 从文件导入
3. 预置变量模板:
   - SVM: ANCHOR_PROVIDER_URL, ANCHOR_WALLET
   - EVM: RPC_URL, PRIVATE_KEY, ETHERSCAN_API_KEY
4. 存储: localStorage (不上传服务端)

## 验收标准

- [ ] 按网络切换环境变量
- [ ] 导入/导出 .env 文件
- [ ] 敏感值遮掩
- [ ] 链切换自动切换 profile

## 不要做

- 不要把 env 存到服务端
- 不要实现 .env.local 自动注入 (用户手动导出)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
