## 目标
在 MCP server 里加 DeFi 协议预置 tool，让 chat 能直接调 Uniswap/Aave/Chainlink

## 约束
- 基于现有 mcp-server TypeScript 架构
- 每个 tool 是独立文件，在 tools/ 目录下
- 用 viem/ethers 调合约，不引入重 SDK

## 实现
1. `tools/uniswap-swap.ts` — 生成 Uniswap V3 swap 调用代码 + 报价查询
2. `tools/aave-lend.ts` — 生成 Aave V3 supply/borrow 调用代码
3. `tools/chainlink-price.ts` — 查询 Chainlink 预言机价格 feed
4. `tools/erc20-toolkit.ts` — approve/transfer/balanceOf 常用操作
5. `tools/defi-registry.ts` — 注册所有 DeFi tool 到 MCP server

## 验收标准
- [ ] 4 个 DeFi tool 文件存在且 TypeScript 编译通过
- [ ] 每个 tool 有 inputSchema 和 execute 方法
- [ ] defi-registry 正确注册所有 tool
- [ ] 有 unit test 验证 inputSchema 合法

## 不要做
- 不做真实链上交互（只生成代码/查询）
- 不改 MCP server 核心架构
- 不加前端 UI