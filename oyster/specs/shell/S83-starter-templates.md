---
task_id: S83-starter-templates
project: shell
priority: 2
estimated_minutes: 30
depends_on: []
modifies: ["mcp-server/templates/erc20-basic/", "mcp-server/templates/nft-collection/", "mcp-server/templates/defi-vault/", "mcp-server/src/tools/create-project.ts", "mcp-server/src/server.ts"]
executor: glm
---

## 目标

创建 3 个 Foundry 项目模板 + `create_project` MCP 工具，让用户一键创建可运行的 Web3 项目。

## 背景

用户进来说 "Create an ERC-20 token"，Shell 应该能立刻创建一个可编译、可测试的 Foundry 项目，而不是只生成一个 .sol 文件。

## 步骤

1. 创建模板目录结构 (每个模板是完整 Foundry 项目):
   ```
   mcp-server/templates/
   ├── erc20-basic/
   │   ├── foundry.toml
   │   ├── src/Token.sol           # 基础 ERC-20 (OpenZeppelin)
   │   ├── test/Token.t.sol        # 完整测试 (mint, burn, transfer)
   │   └── script/Deploy.s.sol     # 部署脚本
   ├── nft-collection/
   │   ├── foundry.toml
   │   ├── src/NFT.sol             # ERC-721 + metadata
   │   ├── test/NFT.t.sol          # mint, tokenURI, ownership 测试
   │   └── script/Deploy.s.sol
   └── defi-vault/
       ├── foundry.toml
       ├── src/Vault.sol           # 简单质押金库 (deposit/withdraw/yield)
       ├── test/Vault.t.sol        # 完整测试含 edge cases
       └── script/Deploy.s.sol
   ```

2. 每个模板的 `foundry.toml`:
   ```toml
   [profile.default]
   src = "src"
   out = "out"
   libs = ["lib"]
   solc = "0.8.24"

   [dependencies]
   forge-std = "1.9.0"
   openzeppelin-contracts = "5.0.0"
   ```

3. 创建 `mcp-server/src/tools/create-project.ts`:
   ```typescript
   name: "create_project"
   description: "Create a new Web3 project from a template. Returns project directory path."
   inputSchema: {
     template: "erc20-basic" | "nft-collection" | "defi-vault" | "blank",
     project_name: string,
     target_dir?: string  // default: /app/projects/{project_name}
   }
   ```
   - 复制模板到目标目录
   - 运行 `forge install` 安装依赖
   - 运行 `forge build` 确认可编译
   - 返回 `{ project_dir, files: string[], build_success: boolean }`

4. 在 server.ts 注册 create_project 工具

## 约束

- 合约代码使用 Solidity 0.8.24
- 使用 OpenZeppelin v5 (最新)
- 测试必须能通过 `forge test`
- 模板不超过 200 行/文件
- 不要用 Hardhat，只用 Foundry

## 验收标准

- [ ] 3 个模板都能 `forge build` 成功
- [ ] 3 个模板都能 `forge test` 全绿
- [ ] create_project 工具创建项目后 build 成功
- [ ] blank 模板创建空 Foundry 项目 (forge init)

## 不要做

- 不要修改 web-ui/
- 不要使用 Hardhat
- 不要写超过 200 行的合约
