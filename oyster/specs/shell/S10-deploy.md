---
task_id: S10-deploy
project: shell-vibe-ide
priority: 1
estimated_minutes: 45
depends_on: ["S08-test-integration", "S09-local-chains"]
modifies: ["web-ui/app/**/*.ts", "web-ui/app/**/*.tsx", "runner/src/index.js"]
executor: glm
---

## 目标

在 IDE 中加入 Deploy 按钮，支持部署到本地链和测试网。

## 步骤

1. 添加 "Deploy" 按钮 (在 Test 按钮旁)
2. 部署目标由网络选择器 (S06) 决定:
   - SVM: localhost / devnet / testnet
   - EVM: anvil (localhost) / sepolia / base-sepolia
3. SVM 部署:
   - `anchor deploy --provider.cluster {network}`
   - 解析输出获取 Program ID
   - 如果是 devnet，先检查 SOL 余额，不够自动 airdrop
4. EVM 部署:
   - `forge create --rpc-url {rpc} src/Contract.sol:ContractName`
   - 或 `forge script script/Deploy.s.sol --rpc-url {rpc} --broadcast`
   - 解析输出获取合约地址 + tx hash
5. 部署成功后:
   - 状态栏显示: `Deployed → {address}`
   - Reports 面板显示部署报告
   - 合约地址可一键复制
   - 链接到区块浏览器 (Solscan / Etherscan)
6. 生成报告: `reports/deploy.{chain}.{network}.json`

## 报告格式

```json
{
  "ok": true,
  "chain": "solana",
  "runner": "anchor",
  "action": "deploy",
  "network": "devnet",
  "summary": "Deployed successfully",
  "details": {
    "programId": "7xK2..mN",
    "txSignature": "5abc..def",
    "explorerUrl": "https://solscan.io/tx/5abc..def?cluster=devnet"
  }
}
```

## 验收标准

- [ ] 点击 Deploy 按钮后终端显示部署输出
- [ ] SVM 部署到 devnet 成功获取 Program ID
- [ ] EVM 部署到 Sepolia 成功获取合约地址
- [ ] 状态栏显示部署地址
- [ ] 部署报告写入 reports/
- [ ] 区块浏览器链接可点击

## 不要做

- 不要实现主网部署 (需要额外安全确认)
- 不要实现合约验证 (Sprint 4+)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
