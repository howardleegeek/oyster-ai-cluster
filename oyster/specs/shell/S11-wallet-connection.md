---
task_id: S11-wallet-connection
project: shell-vibe-ide
priority: 2
estimated_minutes: 45
depends_on: ["S06-chain-selector"]
modifies: ["web-ui/package.json", "web-ui/app/**/*.tsx"]
executor: glm
---

## 目标

在 IDE 中集成钱包连接功能，支持 Solana 和 EVM 钱包。

## 步骤

1. 安装依赖:
   - SVM: `@solana/wallet-adapter-react`, `@solana/wallet-adapter-wallets`, `@solana/wallet-adapter-react-ui`
   - EVM: `wagmi`, `viem`, `@rainbow-me/rainbowkit`
2. 在顶栏右侧加 "Connect Wallet" 按钮
3. SVM 模式:
   - 支持: Phantom, Backpack, Solflare
   - 连接后显示: 地址缩写 + SOL 余额
4. EVM 模式:
   - 支持: MetaMask, WalletConnect, Coinbase Wallet
   - 连接后显示: 地址缩写 + ETH 余额
5. 根据链选择器自动切换钱包 Provider
6. 钱包状态存入全局 context:
   - `walletAddress: string | null`
   - `balance: number`
   - `connected: boolean`
7. 部署时使用连接的钱包签名交易

## UI

```
未连接: [🔗 Connect Wallet]
已连接: [0x1a2b...3c4d | 1.23 SOL] (点击断开)
```

## 验收标准

- [ ] Phantom 钱包可连接 (SVM)
- [ ] MetaMask 钱包可连接 (EVM)
- [ ] 显示地址和余额
- [ ] 切换链时切换钱包 provider
- [ ] 可断开连接
- [ ] 赛博朋克风格的钱包弹窗

## 不要做

- 不要实现交易签名 (部署时再用)
- 不要存储私钥
- 不要实现 WalletConnect v2 深度集成
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
