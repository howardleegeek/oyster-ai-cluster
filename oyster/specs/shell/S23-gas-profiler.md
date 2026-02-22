---
task_id: S23-gas-profiler
project: shell-vibe-ide
priority: 2
estimated_minutes: 40
depends_on: ["S08-test-integration", "S19-evm-debugger"]
modifies: ["web-ui/app/components/gas/gas-profiler.tsx", "web-ui/app/components/gas/gas-heatmap.tsx", "web-ui/app/lib/gas-report-parser.ts"]
executor: glm
---

## 目标

创建 Gas/Compute 分析面板，帮助开发者优化合约成本。

## 步骤

### EVM Gas 分析
1. 从 `forge test --gas-report` 获取 gas 数据
2. 显示每个函数的 gas 消耗:
   - min / avg / max / calls
   - 与上次对比 (增减)
3. Gas 热力图:
   - 在编辑器中用背景色标注高 gas 行
   - 红色 = 高消耗, 绿色 = 低消耗
4. 优化建议 (AI 生成):
   - 检测到高 gas 函数 → AI 建议优化方案

### SVM Compute Unit 分析
1. 从 `anchor test` 日志获取 compute units
2. 显示每个 instruction 的 compute 消耗
3. Solana 交易大小分析 (1232 bytes 限制)

## UI

```
┌─ Gas Profiler ─────────────────────┐
│                                     │
│ Function          avg     max    Δ  │
│ ─────────────────────────────────── │
│ transfer()      34,521  35,000  -2% │
│ approve()       26,100  26,500  +1% │
│ mint()          89,200  90,000  NEW │
│                                     │
│ [Optimize with AI]                  │
│                                     │
│ Total deployment: 1,234,567 gas     │
│ Estimated cost: ~$2.50 @ 20 gwei   │
└─────────────────────────────────────┘
```

## 验收标准

- [ ] EVM: gas report 解析并显示
- [ ] 每个函数的 min/avg/max gas
- [ ] 编辑器 gas 热力图
- [ ] SVM: compute unit 显示
- [ ] AI 优化建议功能
- [ ] 部署成本估算

## 不要做

- 不要实现实时 gas 追踪
- 不要实现 gas 价格 oracle
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
