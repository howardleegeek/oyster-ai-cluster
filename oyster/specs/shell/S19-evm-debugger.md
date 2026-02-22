---
task_id: S19-evm-debugger
project: shell-vibe-ide
priority: 2
estimated_minutes: 50
depends_on: ["S15-remix-compiler"]
modifies: ["web-ui/package.json", "web-ui/app/**/*.tsx"]
executor: glm
---

## 目标

集成 @remix-project/remix-debug 实现 EVM 交易步进调试器。

## 步骤

1. 安装: `pnpm add @remix-project/remix-debug`
2. 创建 Debugger 面板:
   - 输入 tx hash → 加载交易
   - Step forward / backward / into / over
   - 显示: 当前 opcode, stack, memory, storage, call data
   - 源码映射: 高亮当前执行的 Solidity 行
3. 连接到本地 Anvil 节点获取 debug_traceTransaction
4. 断点功能:
   - 在编辑器行号处点击设置断点
   - 运行到断点自动暂停
5. 变量查看:
   - 当前函数的局部变量
   - 合约 storage 变量
   - msg.sender, msg.value, block.number

## UI

```
┌─ EVM Debugger ─────────────────────┐
│ Tx: 0xabc...def                     │
│                                     │
│ [⏮] [⏪] [▶️ Step] [⏩] [⏭]         │
│                                     │
│ Opcode: SSTORE                      │
│ PC: 1234  Gas: 45678                │
│                                     │
│ Stack:                              │
│   0: 0x000...001                    │
│   1: 0x000...abc                    │
│                                     │
│ Storage:                            │
│   slot[0]: 0x123 → 0x456           │
│                                     │
│ [Variables] [Stack] [Memory]         │
└─────────────────────────────────────┘
```

## 验收标准

- [ ] remix-debug 集成成功
- [ ] 可以步进调试本地 Anvil 交易
- [ ] 源码行高亮与 opcode 对应
- [ ] Stack/Memory/Storage 实时显示
- [ ] 断点功能工作

## 不要做

- 不要实现 Solana 调试器 (不同架构)
- 不要实现远程调试 (先只做本地)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
