---
task_id: S22-move-support
project: shell-vibe-ide
priority: 3
estimated_minutes: 50
depends_on: ["S03-dual-syntax-support", "S06-chain-selector"]
modifies: ["web-ui/app/**/*.ts", "web-ui/app/**/*.tsx", "runner/src/index.js", "templates/registry.json"]
executor: glm
---

## 目标

添加 Move 语言支持 (Sui/Aptos)，Shell 成为三链 IDE: SVM + EVM + Move。

## 步骤

1. 链选择器加入 "Move" 选项:
   - Sui: `sui` CLI
   - Aptos: `aptos` CLI
2. Monaco 编辑器加 Move 语法高亮:
   - 关键词: module, struct, fun, public, entry, has, key, store, drop, copy
   - 文件后缀: `.move`
3. Build 集成:
   - Sui: `sui move build`
   - Aptos: `aptos move compile`
4. Test 集成:
   - Sui: `sui move test`
   - Aptos: `aptos move test`
5. Deploy:
   - Sui: `sui client publish --gas-budget 100000000`
   - Aptos: `aptos move publish`
6. 模板 (4 个):
   - Coin (代币)
   - NFT Collection
   - Marketplace
   - Staking
7. Prompt 模板:
   - "Create a Sui Move coin module with mint and burn functions"
   - "Create an Aptos NFT collection with minting"

## 验收标准

- [ ] 链选择器显示 SVM / EVM / Move
- [ ] Move 语法高亮工作
- [ ] Sui build/test 命令集成
- [ ] Move 模板显示在画廊中
- [ ] 部署到 Sui devnet 工作

## 不要做

- 不要实现 Move prover (形式化验证, 太复杂)
- 不要支持旧版 Diem Move
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
