---
task_id: S04-prompt-templates
project: shell-vibe-ide
priority: 2
estimated_minutes: 30
depends_on: ["S01-fork-bolt-diy"]
modifies: ["web-ui/app/**/*.ts", "web-ui/app/**/*.tsx"]
executor: glm
---

## 目标

在 AI Chat 面板中加入 Web3 prompt 模板，用户一键选择即可开始生成合约。

## 模板列表

### SVM (Solana/Anchor)

1. **SPL Token**
   - Prompt: "Create a Solana SPL token program using Anchor. Include mint, transfer, and burn instructions. Use Anchor's #[account] macros for account validation."

2. **NFT Collection**
   - Prompt: "Create a Solana NFT collection program using Anchor with Metaplex standards. Include mint_nft, update_metadata, and verify_collection instructions."

3. **Staking Program**
   - Prompt: "Create a Solana staking program using Anchor. Users can stake SOL, earn rewards over time, and unstake. Include reward calculation based on time staked."

4. **Escrow**
   - Prompt: "Create a Solana escrow program using Anchor. Allow two parties to swap tokens atomically with cancel and execute instructions."

5. **DAO Voting**
   - Prompt: "Create a simple Solana DAO voting program using Anchor. Members can create proposals, vote yes/no, and execute proposals that pass threshold."

### EVM (Solidity/Foundry)

6. **ERC-20 Token**
   - Prompt: "Create an ERC-20 token contract using Solidity 0.8+. Include mint (owner only), burn, and transfer. Use OpenZeppelin's ERC20 base. Add constructor params for name, symbol, and initial supply."

7. **ERC-721 NFT**
   - Prompt: "Create an ERC-721 NFT contract using Solidity 0.8+ with OpenZeppelin. Include safeMint with tokenURI, royalties (ERC-2981), and max supply limit."

8. **Simple Vault**
   - Prompt: "Create a Solidity vault contract that accepts ETH deposits, tracks balances per user, and allows withdrawals. Include emergency withdraw for owner. Use ReentrancyGuard."

9. **DEX (AMM)**
   - Prompt: "Create a simple constant-product AMM (x*y=k) in Solidity. Include addLiquidity, removeLiquidity, and swap functions. Calculate fees at 0.3%."

10. **Governance**
    - Prompt: "Create a Solidity governance contract using OpenZeppelin Governor. Include propose, vote, queue, and execute. Voting period 1 week, quorum 4%."

## UI 实现

1. 在 AI Chat 输入框上方加一排 chip/tag 按钮
2. 按链分组: [SVM] [EVM] 两个 tab
3. 每个模板显示为一个小卡片，包含:
   - 图标 (emoji)
   - 标题 (如 "SPL Token")
   - 一句话描述
4. 点击卡片 → prompt 自动填入聊天输入框
5. 第一次打开 IDE 时显示模板选择面板 (类似 bolt.diy 的起始页)

## 约束

- 模板存储为 JSON 或 TypeScript 常量
- 不要硬编码在 JSX 中
- 保持可扩展 (后续可从 templates/registry.json 加载)

## 验收标准

- [ ] SVM tab 显示 5 个 Solana 模板
- [ ] EVM tab 显示 5 个 EVM 模板
- [ ] 点击模板 → prompt 填入聊天框
- [ ] 模板数据与 UI 分离 (数据在单独文件中)
- [ ] 首次打开显示模板选择面板

## 不要做

- 不要改 AI 模型配置
- 不要改聊天逻辑
- 不要碰 desktop/ 和 runner/
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
