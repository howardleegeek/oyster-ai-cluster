---
task_id: S33-local-explorer
project: shell-vibe-ide
priority: 2
estimated_minutes: 35
depends_on: ["S09-local-chains"]
modifies: ["web-ui/app/components/explorer/local-explorer.tsx", "web-ui/app/components/explorer/tx-list.tsx", "web-ui/app/components/explorer/account-view.tsx", "web-ui/app/lib/explorer/anvil-client.ts"]
executor: glm
---

## 目标

集成本地区块浏览器，在 IDE 内查看本地链的交易和状态。

## 开源方案

- **Otterscan**: github.com/otterscan/otterscan (1.4k stars, MIT) — Anvil 原生支持
- **Solana Explorer**: 可以指向 localhost

## 步骤

### EVM (Otterscan)
1. Anvil 原生支持 Otterscan API
2. 在 IDE 中嵌入 Otterscan:
   - iframe 嵌入 (最简单)
   - 或提取关键组件 (tx list, account view)
3. 功能:
   - 交易列表 (最新在前)
   - 交易详情 (from, to, value, data, logs)
   - 账户余额和交易历史
   - 合约代码查看
   - 内部交易 (internal txs)

### SVM (Solana Explorer)
1. 指向 localhost:8899 的 Solana Explorer
2. 或自建简单面板:
   - 最近交易
   - 账户详情
   - Program logs

## UI

```
┌─ Local Explorer ───────────────────┐
│ [EVM Anvil] [Solana Validator]      │
│                                     │
│ Recent Transactions:                │
│ #1 0xabc...def → 0x123...456       │
│    Transfer 1.0 ETH  ✅ Success     │
│                                     │
│ #2 0xabc...def → Contract           │
│    mint(100)         ✅ Success     │
│                                     │
│ Accounts:                           │
│ 0xabc...def  Balance: 9998.5 ETH   │
│ 0x123...456  Balance: 1001.5 ETH   │
│                                     │
│ [Open Full Explorer ↗]              │
└─────────────────────────────────────┘
```

## 验收标准

- [ ] EVM: Otterscan 或自建面板显示 Anvil 交易
- [ ] SVM: 显示 test-validator 交易
- [ ] 交易详情可查看
- [ ] 账户余额显示
- [ ] 赛博朋克风格

## 不要做

- 不要自己实现区块浏览器 (用 Otterscan)
- 不要实现主网浏览 (用外部浏览器)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
