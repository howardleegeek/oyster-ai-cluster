---
task_id: S27-event-listener
project: shell-vibe-ide
priority: 3
estimated_minutes: 40
depends_on: ["S21-contract-interaction"]
modifies: ["web-ui/app/components/events/event-listener.tsx", "web-ui/app/components/events/event-filters.tsx", "web-ui/app/lib/events/evm-events.ts", "web-ui/app/lib/events/svm-events.ts"]
executor: glm
---

## 目标

创建合约事件监听面板，实时显示链上事件。

## 开源方案

- **wagmi useWatchContractEvent**: 内置 EVM 事件监听
- **@solana/web3.js onAccountChange**: Solana 账户变化监听

## 步骤

1. 事件监听面板:
   - 部署后自动开始监听合约事件
   - EVM: 使用 wagmi 的 `useWatchContractEvent`
   - SVM: 使用 `@solana/web3.js` 的 `onProgramAccountChange`
2. 事件显示:
   - 时间戳 + 事件名 + 参数 + tx hash
   - 实时更新 (WebSocket)
   - 颜色编码: Transfer=绿, Approval=蓝, Error=红
3. 事件过滤:
   - 按事件名
   - 按地址
   - 按时间范围
4. 事件导出:
   - JSON
   - CSV

## UI

```
┌─ Events ───────────────────────────┐
│ Filter: [All Events ▾] [Last 1h ▾] │
│                                     │
│ 12:34:56 Transfer                   │
│   from: 0x1a2b...  to: 0x3c4d...   │
│   amount: 1000 USDC                │
│                                     │
│ 12:34:50 Approval                   │
│   owner: 0x1a2b...                  │
│   spender: 0x5e6f...               │
│   amount: MAX                       │
│                                     │
│ [Export JSON] [Export CSV] [Clear]   │
└─────────────────────────────────────┘
```

## 验收标准

- [ ] EVM 事件实时监听
- [ ] SVM 账户变化监听
- [ ] 事件过滤工作
- [ ] 事件可导出
- [ ] 赛博朋克风格实时更新动画

## 不要做

- 不要实现历史事件查询 (用区块浏览器)
- 不要实现 webhook 通知
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
