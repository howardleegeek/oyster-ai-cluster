---
task_id: S28-evm-bench
project: shell-vibe-ide
priority: 2
estimated_minutes: 45
depends_on: ["S08-test-integration", "S23-gas-profiler"]
modifies: ["web-ui/app/**/*.tsx", "web-ui/package.json"]
executor: glm
---

## 目标

集成 EVM Benchmark 工具，对合约进行性能基准测试。

## 开源方案

- **forge test --gas-report**: Foundry 内置 gas 报告
- **forge snapshot**: 创建 gas 快照用于对比
- **halmos** (github.com/a16z/halmos, 1.1k stars, AGPL-3.0): 符号执行测试
- **echidna** (github.com/crytic/echidna, 2.9k stars, AGPL-3.0): 模糊测试
- **medusa** (github.com/crytic/medusa, 600+ stars, AGPL-3.0): Go-based fuzzer

## 步骤

1. Benchmark 面板:
   - 运行 `forge test --gas-report` → 解析 gas 数据
   - 运行 `forge snapshot` → 创建基准快照
   - 运行 `forge snapshot --diff` → 与上次对比
2. Fuzz Testing 集成:
   - Foundry fuzz: `forge test --fuzz-runs 1000`
   - 显示: 测试名 + runs + 失败的 counterexample
   - 可配置 fuzz runs 数量
3. 性能对比:
   - 存储每次 benchmark 结果
   - 图表显示趋势 (gas 随版本变化)
   - 检测回归 (gas 增加超过 5% 警告)
4. EVM Bench 报告:
   ```json
   {
     "ok": true,
     "action": "benchmark",
     "chain": "evm",
     "details": {
       "gasReport": [...],
       "snapshot": {...},
       "fuzzResults": [...],
       "comparison": {
         "previous": "...",
         "changes": [
           {"function": "transfer", "before": 34521, "after": 35000, "delta": "+1.4%"}
         ]
       }
     }
   }
   ```
5. UI:
   - Gas 对比表格 (function, before, after, Δ%)
   - Fuzz 结果面板
   - 趋势图 (简单 sparkline)

## UI

```
┌─ EVM Benchmark ────────────────────┐
│                                     │
│ Gas Snapshot Diff:                  │
│ Function      Before  After   Δ%   │
│ transfer()   34,521  35,000  +1.4% │
│ approve()    26,100  26,050  -0.2% │
│ mint()        ---    89,200   NEW  │
│                                     │
│ Fuzz Testing (1000 runs):           │
│ ✅ test_transfer_fuzz   1000/1000   │
│ ✅ test_approve_fuzz    1000/1000   │
│ ❌ test_overflow_fuzz   failed@998  │
│   Counterexample: amount=2^256-1   │
│                                     │
│ [Run Benchmark] [Compare] [Export]  │
└─────────────────────────────────────┘
```

## 验收标准

- [ ] forge gas-report 解析并显示
- [ ] forge snapshot 创建和对比
- [ ] Fuzz testing 集成 (显示 runs + counterexample)
- [ ] Gas 变化趋势存储
- [ ] Gas 回归检测 (>5% 警告)
- [ ] 报告导出

## 不要做

- 不要自己实现 fuzzer (用 Foundry 内置)
- 不要实现 Solana benchmark (不同架构)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
