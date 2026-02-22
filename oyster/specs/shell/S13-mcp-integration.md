---
task_id: S13-mcp-integration
project: shell-vibe-ide
priority: 2
estimated_minutes: 45
depends_on: ["S06-chain-selector"]
modifies: ["web-ui/app/**/*.ts", "desktop/mcp-servers.json"]
executor: glm
---

## 目标

集成 MCP servers，让 AI 可以直接与链上交互（查余额、airdrop、读合约等）。

## MCP Servers

### Solana
- **solana-mcp** (sendaifun/solana-mcp): Apache-2.0
- 安装: `npx solana-mcp`
- 能力: wallet ops, SPL tokens, NFT minting, TPS metrics

### EVM
- **evm-mcp-server** (mcpdotdirect/evm-mcp-server): MIT
- 安装: `npx evm-mcp-server`
- 能力: balances, contract reads/writes, ERC-20/721/1155, ENS, 60+ networks

## 步骤

1. 更新 `desktop/mcp-servers.json`:
   - 替换现有的 solana/evm 配置为上述开源 MCP servers
2. 在 AI Chat 中注册 MCP tools:
   - bolt.diy 已有 MCP 支持 → 配置 server 连接
3. SVM 模式下自动启动 solana-mcp
4. EVM 模式下自动启动 evm-mcp-server
5. AI 可以在对话中调用链上工具:
   - "Check my SOL balance" → 调用 solana-mcp 的 getBalance
   - "Airdrop 2 SOL" → 调用 solana-mcp 的 requestAirdrop
   - "Read USDC balance for 0x..." → 调用 evm-mcp 的 getBalance
6. Desktop: Tauri 管理 MCP server 进程
7. Web: 通过 API proxy 连接

## 验收标准

- [ ] mcp-servers.json 配置了 solana-mcp 和 evm-mcp-server
- [ ] AI Chat 中可调用 MCP tools
- [ ] 可以查询 Solana 余额
- [ ] 可以在 devnet 请求 airdrop
- [ ] 可以查询 EVM 余额
- [ ] 切换链时切换 MCP server

## 不要做

- 不要自己实现链上交互 (用 MCP servers)
- 不要改 AI 核心逻辑
- 不要实现交易签名 (钱包负责)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
