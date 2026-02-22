## 目标

建立完整的测试套件，覆盖 runner、web-ui 组件、和 MCP server 三层。

## 步骤

1. **Runner 单元测试** — `runner/tests/`:
   - `detect.test.js` — 测试项目类型检测 (EVM vs Solana)
   - `test-runner.test.js` — 测试 `shell-run test` 命令
   - `build-runner.test.js` — 测试 `shell-run build` 命令
   - `report-writer.test.js` — 测试报告 JSON schema 合规

2. **Web-UI 组件测试** — `web-ui/__tests__/`:
   - `ChainSelector.test.tsx` — 链选择器交互
   - `TestResultsPanel.test.tsx` — 测试结果面板渲染
   - `FaucetPanel.test.tsx` — Faucet 交互
   - `UpgradeWizard.test.tsx` — 升级向导流程

3. **CI 集成** — 更新 `.github/workflows/test.yml`:
   ```yaml
   jobs:
     runner-tests:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-node@v4
         - run: cd runner && npm test
     web-ui-tests:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - run: cd web-ui && pnpm install && pnpm test
   ```

## 约束

- Runner 测试用 Node.js 内置 test runner (node:test)
- Web-UI 测试用 Vitest + React Testing Library
- 所有测试必须可在 CI 中运行 (无浏览器依赖)
- Mock 外部依赖 (Foundry, Anchor, Anvil)

## 验收标准

- [ ] Runner: 4 个测试文件全部 pass
- [ ] Web-UI: 4 个组件测试全部 pass
- [ ] CI workflow 语法正确
- [ ] 无需本地工具链即可运行测试

## 不要做

- 不要写 E2E 浏览器测试 (交给 S84)
- 不要修改组件实现代码