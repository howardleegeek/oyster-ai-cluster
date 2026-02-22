---
task_id: S87-gas-profiler-tool
project: shell
priority: 3
estimated_minutes: 25
depends_on: ["S71-mcp-server-scaffold", "S72-forge-test-tool"]
modifies: ["mcp-server/src/tools/gas-profiler.ts", "mcp-server/src/server.ts"]
executor: glm
---

## 目标

实现 `gas_profiler` MCP 工具，分析合约的 gas 消耗并给出优化建议。

## 步骤

1. 创建 `mcp-server/src/tools/gas-profiler.ts`:
   ```typescript
   name: "gas_profiler"
   description: "Profile gas usage of smart contract functions and suggest optimizations."
   inputSchema: {
     project_dir: string,
     contract_name?: string  // 指定合约 (默认全部)
   }
   ```
2. 执行 `forge test --gas-report --json`
3. 解析 gas report:
   ```typescript
   {
     contracts: [{
       name: string,
       functions: [{
         name: string,
         calls: number,
         avg_gas: number,
         median_gas: number,
         min_gas: number,
         max_gas: number
       }]
     }],
     total_gas: number,
     optimization_hints: [{
       function_name: string,
       current_gas: number,
       hint: string,
       category: "storage" | "loop" | "calldata" | "packing" | "other",
       estimated_savings: string
     }]
   }
   ```
4. 优化建议规则:
   - gas > 50000 且有 SSTORE → "Consider using immutable or constant"
   - gas > 100000 且有循环 → "Consider bounding loop iterations"
   - 多个 small variables → "Consider variable packing"
   - bytes memory → "Consider using calldata for read-only params"

## 约束

- 纯规则匹配优化建议 (不调 LLM)
- estimated_savings 是粗略百分比范围

## 验收标准

- [ ] 返回每个函数的 gas 消耗
- [ ] 至少 4 种优化建议类别
- [ ] 无 forge 测试时返回友好错误

## 不要做

- 不要调用 LLM
- 不要修改 web-ui/
