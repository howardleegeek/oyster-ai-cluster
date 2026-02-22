---
task_id: S49-fuzz-testing
project: shell-vibe-ide
priority: 2
estimated_minutes: 30
depends_on: ["S08-test-integration", "S05-build-integration"]
modifies: ["web-ui/app/components/workbench/FuzzPanel.tsx", "web-ui/app/lib/stores/fuzz.ts", "runner/src/fuzz.js"]
executor: glm
---

## 目标

集成 Foundry invariant/fuzz 测试到 IDE，一键运行 `forge test --fuzz-runs 1000`，结果展示在 FuzzPanel。

## 步骤

1. 新建 `web-ui/app/lib/stores/fuzz.ts`:
   - nanostores atom: `fuzzStatus` (idle/running/done/error)
   - `fuzzResults`: { totalRuns, failures, counterexamples }
2. 新建 `web-ui/app/components/workbench/FuzzPanel.tsx`:
   - 显示 fuzz 运行状态、进度条
   - 失败时展示 counterexample 详情
   - "Run Fuzz" 按钮，可配置 runs 数量 (100/1000/10000)
3. `runner/src/fuzz.js`:
   - 执行 `forge test --match-contract Invariant --fuzz-runs <N>`
   - 解析输出为 JSON 报告写入 `reports/fuzz.*.json`
4. 新建 Remix route `api.fuzz.ts`:
   - POST: 启动 fuzz 测试
   - GET: 返回最新 fuzz 报告

## 验收标准

- [ ] 可配置 fuzz runs 数量
- [ ] 执行后生成 JSON 报告
- [ ] UI 展示 counterexample
- [ ] 符合 report-driven workflow

## 不要做

- 不要实现自定义 fuzzer，直接用 Foundry 内置的
- 不要碰已有的 test 组件
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
