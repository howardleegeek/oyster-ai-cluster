---
task_id: S51-tx-simulator
project: shell-vibe-ide
priority: 2
estimated_minutes: 30
depends_on: ["S09-local-chains", "S21-contract-interaction"]
modifies: ["web-ui/app/components/workbench/TxSimulator.tsx", "web-ui/app/lib/stores/simulator.ts"]
executor: glm
---

## 目标

交易模拟器：在本地链上模拟交易，展示 state diff、gas 消耗、事件日志，不实际上链。

## 步骤

1. `web-ui/app/lib/stores/simulator.ts`:
   - `simulationResult`: { gasUsed, stateDiff[], events[], returnValue, revertReason? }
   - `simulationStatus`: idle | simulating | done | error
2. `web-ui/app/components/workbench/TxSimulator.tsx`:
   - 输入区: to, value, calldata (或从 ABI 选函数+参数)
   - 结果区:
     - Gas 消耗 (数值 + 可视条)
     - State Diff 表格 (slot, before, after)
     - 事件日志列表
     - Revert reason (如果失败)
   - "Simulate" 按钮
3. Remix route `api.simulate.ts`:
   - POST: 调用本地 Anvil 的 `eth_call` 或 `debug_traceCall`
   - 解析 trace 数据返回结构化结果
4. SVM 模式:
   - 调用 `solana simulate-transaction` 或 RPC `simulateTransaction`

## 验收标准

- [ ] EVM: 显示 gas、state diff、events
- [ ] SVM: 显示 compute units、logs
- [ ] 失败交易显示 revert reason
- [ ] 不实际修改链上状态

## 不要做

- 不要实现 trace 可视化 (S19 的 debugger 做)
- 不要连远程 RPC，只用本地链
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
