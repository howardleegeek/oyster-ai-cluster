# Shell v2 方向 — 对标 Noah AI

> 日期: 2026-02-22
> 来源: Howard 竞品分析 + Opus 审计

## 定位
Shell = Noah 的 Pro 版 + 开发者工具链
Noah = Canva (人人能用)
Shell = Figma (专业人士首选，但新手也能上手)

## 三大方向

### 1. "Chat → Live Link" 闭环 (P0)
Noah 最大杀手锏：prompt → 2 分钟拿到可分享 live URL。
Shell 已有所有组件 (chat + 合约 + 部署)，但没串起来。
→ 加 "Quick Launch" 模式：对话生成合约+前端 → 自动部署 Vercel/IPFS → 返回 live link

### 2. DeFi 协议 SDK 内置 (P1)
Noah 集成 Jupiter/Raydium/Meteora，用户说 "建 swap 页面" 直接调 API。
→ MCP server 加 Uniswap/Aave/Chainlink 预置 tool

### 3. 后端即服务 Supabase (P1)
dApp 不只合约+前端，还需要用户系统、数据存储。
→ 集成 Supabase/Firebase，模板自带 auth + 数据层

## Shell 独有优势 (加强不放弃)
- IDE + Terminal + Debugger 深度
- MCP 协议标准化
- Tauri 桌面端 (离线 + 本地密钥)
- Foundry/Hardhat 生产级测试

## 审计发现的 P0 修复
- web-ui/tsconfig.json JSON 注释
- web-ui/package.json 重复 scripts key
- deploy.config.sample.json JSON 注释
- mcp-server/package.json 缺 SDK 依赖
- runner/ 缺 package.json
