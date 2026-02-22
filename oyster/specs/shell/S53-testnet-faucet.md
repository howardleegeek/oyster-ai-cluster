---
task_id: S53-testnet-faucet
project: shell-vibe-ide
priority: 2
estimated_minutes: 20
depends_on: ["S06-chain-selector", "S11-wallet-connection"]
modifies: ["web-ui/app/components/workbench/FaucetPanel.tsx", "web-ui/app/lib/stores/faucet.ts"]
executor: glm
---

## 目标

集成测试网水龙头：从 IDE 内直接请求测试代币，支持 Solana devnet SOL 和 EVM Sepolia ETH。

## 步骤

1. `web-ui/app/lib/stores/faucet.ts`:
   - nanostores atom: `faucetStatus` (idle/requesting/success/error)
   - `faucetHistory`: 最近 10 次请求记录 [{chain, network, amount, txHash, timestamp}]
2. `web-ui/app/components/workbench/FaucetPanel.tsx`:
   - 根据当前 chainType + network 自动选择水龙头
   - SVM devnet: 调用 `connection.requestAirdrop(pubkey, 2 * LAMPORTS_PER_SOL)`
   - EVM Sepolia: 显示外部水龙头链接 (Alchemy/Infura faucet URL)
   - EVM Anvil: 直接 `eth_sendTransaction` 从 Anvil 预充值账户转
   - 显示请求历史和余额
3. 支持的网络:
   - Solana devnet: 原生 airdrop API
   - Solana testnet: 原生 airdrop API
   - Anvil: 本地 ETH 转账
   - Sepolia/Base-Sepolia: 外链到水龙头网站

## 验收标准

- [ ] Solana devnet airdrop 可用
- [ ] Anvil 本地 ETH 可领取
- [ ] 外部水龙头链接正确
- [ ] 请求历史可查看

## 不要做

- 不要实现自建水龙头服务端
- 不要存私钥
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
