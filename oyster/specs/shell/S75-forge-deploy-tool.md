---
task_id: S75-forge-deploy-tool
project: shell
priority: 2
estimated_minutes: 35
depends_on: ["S71-mcp-server-scaffold", "S73-forge-build-tool"]
modifies: ["mcp-server/src/tools/forge-deploy.ts", "mcp-server/src/server.ts"]
executor: glm
---

## 目标

实现 `forge_deploy` MCP 工具，能将编译好的合约部署到 Anvil 本地链或测试网。

## 步骤

1. 创建 `mcp-server/src/tools/forge-deploy.ts`:
   ```typescript
   name: "forge_deploy"
   description: "Deploy a compiled contract to Anvil (local) or testnet."
   inputSchema: {
     project_dir: string,
     contract_name: string,       // 要部署的合约名
     constructor_args?: string[], // 构造函数参数
     chain: "anvil" | "sepolia" | "base-sepolia" | "custom",
     rpc_url?: string,           // custom chain 的 RPC
     private_key?: string,       // 部署账户私钥 (Anvil 用默认)
     verify?: boolean            // 是否验证 (仅测试网)
   }
   ```
2. Anvil 部署 (默认):
   - 检查 Anvil 是否在跑 (curl http://127.0.0.1:8545)
   - 使用 Anvil 默认账户: `0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80`
   - 执行 `forge script` 或 `forge create`
3. 测试网部署:
   - 需要 private_key 和 rpc_url
   - 执行 `forge create --rpc-url {rpc_url} --private-key {key}`
4. 返回:
   ```typescript
   {
     success: boolean,
     address: string,        // 部署的合约地址
     tx_hash: string,
     chain: string,
     block_number: number,
     gas_used: number,
     deployer: string,
     constructor_args: string[]
   }
   ```

## 约束

- Anvil 私钥是公开的测试私钥，可以硬编码
- 测试网私钥必须由用户提供，不要生成或存储
- 部署超时: 60 秒 (Anvil), 300 秒 (测试网)
- 如果 Anvil 未启动，返回错误和启动命令提示

## 验收标准

- [ ] Anvil 部署: 返回合约地址
- [ ] 带构造函数参数的部署正常工作
- [ ] Anvil 未启动时返回友好错误

## 不要做

- 不要部署到主网 (只支持 Anvil + 测试网)
- 不要存储私钥
- 不要修改 web-ui/
