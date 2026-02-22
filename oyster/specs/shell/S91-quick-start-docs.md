---
task_id: S91-quick-start-docs
project: shell
priority: 2
estimated_minutes: 25
depends_on: []
modifies: ["README.md", "docs/QUICKSTART.md"]
executor: glm
---

## 目标

写一份 Quick Start 文档，让新用户 5 分钟内跑通 Shell 的核心功能。

## 步骤

1. **更新 `README.md`**:
   - 添加 Quick Start 部分链接到 `docs/QUICKSTART.md`
   - 添加功能特性列表 (带截图占位符)
   - 添加 Architecture diagram (ASCII)
   - 添加 badge: CI status, license

2. **创建 `docs/QUICKSTART.md`**:
   ```markdown
   # Quick Start

   ## Prerequisites
   - Node.js 20+
   - pnpm
   - Foundry (for EVM development)
   - Anchor (for Solana development, optional)

   ## Option 1: Web UI
   ```bash
   cd web-ui
   pnpm install
   pnpm dev
   # Open http://localhost:5173
   ```

   ## Option 2: CLI Runner
   ```bash
   cd demo/evm-vault
   node ../../runner/src/index.js test --chain evm
   cat reports/test.evm.forge.json
   ```

   ## Option 3: MCP Server
   ```bash
   cd mcp-server
   bun install
   bun run src/server.ts
   ```

   ## Your First Smart Contract
   1. Open Shell web UI
   2. Select "ERC-20 Token" template
   3. Click "Build" → "Test" → "Deploy to Anvil"
   4. Check reports/ for results
   ```

3. **创建 `docs/FEATURES.md`**: 简要列出所有已实现功能

## 约束

- 文档必须准确反映当前代码状态
- 命令必须可实际执行
- 不要编造未实现的功能

## 验收标准

- [ ] README.md 包含 Quick Start 链接和功能列表
- [ ] QUICKSTART.md 的 3 个 Option 命令都可执行
- [ ] 无断链或引用不存在的文件
- [ ] Markdown 格式正确 (lint 通过)

## 不要做

- 不要写 API 文档 (后续再做)
- 不要添加截图 (只放占位符)
