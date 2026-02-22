---
task_id: S01-web3-defi-scan
project: open-source-research
priority: 1
estimated_minutes: 30
depends_on: []
modifies: ["research/web3-defi-scan.md"]
executor: codex
---

## 目标
搜索 GitHub 上最佳的 Web3/DeFi 开源项目，为 Oyster Labs 以下项目找到可直接 Fork 使用的替代方案。

## 搜索清单

请对以下每个项目搜索 GitHub，找到 TOP 3 最佳开源替代：

1. **参数化加密保险** — 搜索: "parametric insurance solidity", "defi insurance protocol", "crypto insurance smart contract"
2. **预测市场+永续合约** — 搜索: "prediction market smart contract", "perpetual futures dex open source"
3. **自定义 AMM** — 搜索: "automated market maker solidity", "custom AMM hook", "uniswap v4 hooks"
4. **链上外汇** — 搜索: "onchain forex trading", "synthetic forex solidity", "leveraged trading protocol"
5. **消费级 DeFi 钱包** — 搜索: "defi wallet open source react native", "crypto wallet app open source"
6. **隐私链工具** — 搜索: "privacy blockchain tools", "zero knowledge smart contract", "ZK rollup"
7. **DePIN 工具** — 搜索: "depin framework", "decentralized physical infrastructure"
8. **预言机** — 搜索: "blockchain oracle open source", "price feed oracle"
9. **NFT 估值 AI** — 搜索: "nft valuation machine learning", "nft price prediction"
10. **AI 量化交易** — 搜索: "crypto trading bot python ml", "ai trading framework"
11. **去中心化算力市场** — 搜索: "decentralized compute marketplace", "gpu marketplace blockchain"
12. **Web3 SDK** — 搜索: "web3 sdk typescript", "blockchain sdk ai"

## 输出格式

对每个项目，输出 Markdown 表格：

```markdown
### [项目名称]

| Repo | Stars | 最后更新 | License | 语言 | 匹配度 | 推荐用法 |
|------|-------|---------|---------|------|--------|---------|
| owner/repo | 数字 | YYYY-MM | 许可证 | 语言 | 高/中/低 | Fork/集成/参考 |
```

附简短说明：为什么推荐，怎么用。

## 约束
- 只搜索 Stars > 100 且最近 12 个月有更新的项目
- 优先 Apache-2.0 / MIT license
- 每个类别至少找 3 个候选
- 输出到 `research/web3-defi-scan.md`

## 验收标准
- [ ] 12 个类别都有搜索结果
- [ ] 每个类别至少 3 个候选项目
- [ ] 包含 Stars、License、最后更新信息
- [ ] 有推荐用法说明
