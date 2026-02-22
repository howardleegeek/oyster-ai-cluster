---
task_id: S76-chain-status-tool
project: shell
priority: 3
estimated_minutes: 20
depends_on: ["S71-mcp-server-scaffold"]
modifies: ["mcp-server/src/tools/chain-status.ts", "mcp-server/src/server.ts"]
executor: glm
---

## 目标

实现 `chain_status` MCP 工具，检查本地/远程区块链状态。

## 步骤

1. 创建 `mcp-server/src/tools/chain-status.ts`:
   ```typescript
   name: "chain_status"
   description: "Check blockchain node status. Works with Anvil, Hardhat Network, and remote RPCs."
   inputSchema: {
     chain?: "anvil" | "hardhat" | "custom",
     rpc_url?: string  // default: http://127.0.0.1:8545
   }
   ```
2. 通过 JSON-RPC 调用:
   - `eth_blockNumber` → 当前区块高度
   - `eth_chainId` → chain ID
   - `eth_accounts` → 可用账户列表
   - `net_version` → 网络版本
   - `eth_gasPrice` → 当前 gas 价格
3. 返回:
   ```typescript
   {
     online: boolean,
     chain_id: number,
     block_number: number,
     accounts: string[],
     gas_price: string,
     rpc_url: string,
     node_type: "anvil" | "hardhat" | "geth" | "unknown"
   }
   ```
4. 节点类型检测: 通过 `web3_clientVersion` 判断

## 约束

- 只用原生 fetch (不依赖 ethers/viem)
- 超时 5 秒
- 离线时返回 `{ online: false, error: "..." }`

## 验收标准

- [ ] Anvil 运行时返回完整状态
- [ ] 节点离线时返回 online: false
- [ ] chain_id 和 block_number 正确

## 不要做

- 不要安装 ethers 或 viem
- 不要修改 web-ui/
