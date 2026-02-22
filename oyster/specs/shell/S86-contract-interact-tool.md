---
task_id: S86-contract-interact-tool
project: shell
priority: 2
estimated_minutes: 35
depends_on: ["S71-mcp-server-scaffold", "S73-forge-build-tool"]
modifies: ["mcp-server/src/tools/contract-interact.ts", "mcp-server/src/server.ts"]
executor: glm
---

## 目标

实现 `contract_interact` MCP 工具，让 AI 能调用已部署合约的函数。

## 背景

部署完合约后，用户会说 "mint 1000 tokens to my address" 或 "check my balance"。AI 需要能直接调用合约函数并返回结果。这让 Shell 从 "只能写代码" 变成 "能操作链上状态"。

## 步骤

1. 创建 `mcp-server/src/tools/contract-interact.ts`:
   ```typescript
   name: "contract_interact"
   description: "Call a function on a deployed smart contract."
   inputSchema: {
     address: string,             // 合约地址
     abi: object[] | string,      // ABI (JSON array 或文件路径)
     function_name: string,       // 函数名
     args?: any[],                // 参数
     value?: string,              // 发送 ETH (wei)
     from?: string,               // 调用者地址
     call_type: "read" | "write"  // view 函数 vs 状态修改
   }
   ```
2. 实现:
   - `read` (view/pure): 使用 `cast call`
   - `write` (状态修改): 使用 `cast send`
   - 解析返回值为人类可读格式
   - gas 估算: 使用 `cast estimate`
3. 使用 `cast` 命令行 (Foundry 自带):
   - `cast call {addr} "balanceOf(address)" {arg} --rpc-url http://127.0.0.1:8545`
   - `cast send {addr} "mint(address,uint256)" {to} {amount} --private-key {key} --rpc-url ...`
4. 返回:
   ```typescript
   {
     success: boolean,
     result?: any,            // 解码后的返回值
     raw_result?: string,     // 原始 hex
     tx_hash?: string,        // write 操作的交易 hash
     gas_used?: number,
     events?: { name, args }[] // 触发的事件
   }
   ```

## 约束

- 只使用 cast (不依赖 ethers/viem)
- write 操作默认使用 Anvil 第一个账户
- 必须 decode 返回值 (不返回原始 hex)
- 事件日志自动解析

## 验收标准

- [ ] read: 调用 ERC-20 balanceOf 返回余额
- [ ] write: 调用 ERC-20 mint 成功并返回 tx hash
- [ ] events: mint 后能看到 Transfer 事件
- [ ] 错误: 调用不存在的函数返回清晰错误

## 不要做

- 不要安装 ethers 或 viem
- 不要修改 web-ui/
