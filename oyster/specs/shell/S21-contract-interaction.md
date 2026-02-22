---
task_id: S21-contract-interaction
project: shell-vibe-ide
priority: 2
estimated_minutes: 50
depends_on: ["S10-deploy", "S11-wallet-connection"]
modifies: ["web-ui/app/components/contract/contract-interaction.tsx", "web-ui/app/components/contract/function-form.tsx", "web-ui/app/components/contract/tx-history.tsx", "web-ui/app/lib/abi-parser.ts"]
executor: glm
---

## 目标

创建合约交互 UI，让用户可以直接从 IDE 调用已部署合约的函数。

## 步骤

1. 部署成功后自动打开合约交互面板
2. EVM 合约交互:
   - 从编译输出获取 ABI
   - 或用 WhatsABI (`pnpm add @shazow/whatsabi`) 从地址推断
   - 渲染每个函数为表单:
     - Read 函数 (view/pure): 直接调用，显示返回值
     - Write 函数: 需要钱包签名
   - 参数输入: 根据类型渲染 (address, uint256, bool, bytes, etc.)
3. SVM 合约交互:
   - 从 IDL (Anchor Interface Description) 获取接口
   - 渲染每个 instruction 为表单
   - Account 参数自动推断 (PDA 计算)
4. 交易结果:
   - 成功: 显示返回值 + tx hash + gas used
   - 失败: 显示 revert reason
5. 历史记录:
   - 最近 20 笔交互
   - 可重放 (re-execute with same params)

## UI

```
┌─ Contract: 0x1a2b...3c4d ──────────┐
│                                      │
│ Read Functions:                      │
│ ┌─ balanceOf(address) ─────────────┐ │
│ │ address: [0x...          ] [Call] │ │
│ │ Result: 1000000000               │ │
│ └──────────────────────────────────┘ │
│                                      │
│ Write Functions:                     │
│ ┌─ transfer(address, uint256) ─────┐ │
│ │ to:     [0x...          ]        │ │
│ │ amount: [100            ]        │ │
│ │              [Send Transaction]  │ │
│ └──────────────────────────────────┘ │
└──────────────────────────────────────┘
```

## 验收标准

- [ ] EVM: ABI 解析并渲染函数列表
- [ ] EVM: Read 函数可调用查看返回值
- [ ] EVM: Write 函数可通过钱包签名发送
- [ ] SVM: IDL 解析并渲染 instruction 列表
- [ ] 交易结果显示 (成功/失败)
- [ ] 交互历史记录

## 不要做

- 不要实现 event 监听 (后续做)
- 不要实现批量调用
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
