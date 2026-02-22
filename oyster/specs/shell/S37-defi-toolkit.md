---
task_id: S37-defi-toolkit
project: shell-vibe-ide
priority: 3
estimated_minutes: 50
depends_on: ["S21-contract-interaction", "S13-mcp-integration"]
modifies: ["web-ui/app/**/*.tsx", "web-ui/package.json"]
executor: glm
---

## 目标

创建 DeFi 专业工具包：流动性分析、价格预言机集成、闪电贷模拟。

## 开源方案

- **GOAT SDK**: github.com/goat-sdk/goat (950 stars, MIT) — 200+ DeFi 工具 (Uniswap, Aave, Jupiter)
- **Scaffold-ETH 2**: DeFi 组件和 hooks
- **Jupiter SDK**: Solana DEX 聚合
- **Pyth Network SDK**: 价格预言机

## 步骤

1. DeFi 面板:
   - Token 价格查询 (Pyth/Chainlink)
   - 流动性池分析 (Uniswap/Raydium)
   - TVL 追踪
2. DeFi 模板 (新增):
   - Flash Loan Arbitrage (EVM)
   - Yield Farming (EVM)
   - Jupiter Swap Integration (SVM)
   - Lending Pool (EVM)
   - LP Token Staking (SVM)
3. 价格预言机集成:
   - Pyth (SVM + EVM)
   - Chainlink (EVM)
   - 代码模板: "集成 Pyth 价格 feed"
4. 闪电贷模拟:
   - 在 Anvil 上模拟闪电贷交易
   - 显示: 借入 → 操作 → 还款 + 利润
5. Impermanent Loss 计算器:
   - 输入: token pair, 价格变化
   - 输出: IL 百分比, 图表

## 验收标准

- [ ] DeFi 面板显示 token 价格
- [ ] 5 个新 DeFi 模板
- [ ] Pyth 价格 feed 集成示例
- [ ] 闪电贷模拟工作
- [ ] IL 计算器

## 不要做

- 不要接入真实交易 (只模拟)
- 不要给投资建议
- 不要存储用户资产信息
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
