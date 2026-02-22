---
task_id: S05-build-integration
project: shell-vibe-ide
priority: 2
estimated_minutes: 45
depends_on: ["S01-fork-bolt-diy", "S03-dual-syntax-support"]
modifies: ["web-ui/app/**/*.ts", "web-ui/app/**/*.tsx", "runner/src/index.js"]
executor: glm
---

## 目标

在 IDE 中加入 Build 按钮，根据选择的链调用 `anchor build` (SVM) 或 `forge build` (EVM)，结果显示在终端面板。

## 步骤

1. 在 UI 中添加一个 "Build" 按钮 (位于编辑器工具栏或 AI Chat 的 action 区域)
2. 根据当前项目/链类型判断调用哪个命令:
   - SVM: `anchor build`
   - EVM: `forge build`
3. 调用方式:
   - Web App: 通过 `/api/shell-run` endpoint (已有)
   - Desktop: 通过 Tauri invoke `run_web3_command` (已有)
4. 输出流式显示在终端面板中
5. 构建完成后生成报告:
   - 成功: `reports/build.solana.anchor.json` 或 `reports/build.evm.forge.json`
   - 包含: `{ok, chain, runner, command, exitCode, summary, stdout, stderr}`
6. 状态栏显示构建状态: Building... → Build ✓ 或 Build ✗

## 报告格式

```json
{
  "ok": true,
  "chain": "solana",
  "runner": "anchor",
  "action": "build",
  "startedAt": "2026-02-21T00:00:00Z",
  "finishedAt": "2026-02-21T00:00:12Z",
  "command": "anchor build",
  "exitCode": 0,
  "summary": "Build successful",
  "details": {
    "programId": "7xK2...",
    "artifacts": ["target/deploy/my_program.so"]
  }
}
```

## 约束

- 复用现有 `runner/src/index.js` (shell-run) 的逻辑
- 复用现有 `desktop/src-tauri/commands.rs` 的 `run_web3_command`
- 报告格式遵循 `schemas/test-report.schema.json` 的基本结构
- 不要改 runner 的核心逻辑，只扩展

## 验收标准

- [ ] 点击 Build 按钮后终端显示构建输出
- [ ] SVM 项目调用 `anchor build`
- [ ] EVM 项目调用 `forge build`
- [ ] 构建完成后生成 JSON 报告
- [ ] 状态栏显示构建状态 (成功/失败)
- [ ] 构建失败时终端显示错误信息

## 不要做

- 不要实现 test/deploy (S08, S10 做)
- 不要实现 auto-repair (Sprint 2 做)
- 不要改 runner 的 detect 逻辑
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
