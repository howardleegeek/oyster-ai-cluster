---
task_id: S42-multi-chain-deploy
project: shell-vibe-ide
priority: 2
estimated_minutes: 40
depends_on: ["S10-deploy", "S35-contract-verification"]
modifies: ["web-ui/app/components/deploy/multi-chain-deploy.tsx", "web-ui/app/components/deploy/deploy-status.tsx", "web-ui/app/lib/deploy/batch-deployer.ts", "web-ui/app/lib/deploy/deploy-config.ts"]
executor: glm
---

## 目标

一键部署到多个链：选择多个目标链和网络，批量部署。

## 开源方案

- **Foundry forge script**: 多链部署脚本
- **Hardhat deploy**: github.com/wighawag/hardhat-deploy (2.3k stars)

## 步骤

1. 多链部署向导:
   - 选择合约
   - 勾选目标网络 (可多选):
     - EVM: Sepolia, Base Sepolia, Arbitrum Sepolia, Polygon Amoy
     - SVM: Devnet, Testnet
   - 配置每个网络的参数 (constructor args, gas price)
2. 批量部署:
   - 并行部署到所有选中网络
   - 每个网络的状态实时更新
   - 失败的重试
3. 部署结果:
   - 所有部署地址的汇总表
   - 每个网络的 tx hash + explorer 链接
   - 一键全部验证 (Sourcify)
4. 部署配置文件:
   - 保存部署配置为 `deploy.config.json`
   - 可重复使用

## UI

```
┌─ Multi-Chain Deploy ───────────────┐
│                                     │
│ Contract: MyToken.sol               │
│                                     │
│ ☑ Sepolia          Deploying...  ⏳ │
│ ☑ Base Sepolia     ✅ 0x1a2b...    │
│ ☑ Arbitrum Sepolia ✅ 0x3c4d...    │
│ ☐ Polygon Amoy                     │
│ ☑ Solana Devnet    ✅ 7xK2...      │
│                                     │
│ [Deploy All] [Verify All]           │
└─────────────────────────────────────┘
```

## 验收标准

- [ ] 可选择多个目标网络
- [ ] 并行部署
- [ ] 实时状态更新
- [ ] 部署汇总表
- [ ] 一键验证

## 不要做

- 不要实现主网部署 (需要额外安全层)
- 不要实现 cross-chain messaging
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
