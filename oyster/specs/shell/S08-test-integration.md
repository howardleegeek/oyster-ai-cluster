---
task_id: S08-test-integration
project: shell-vibe-ide
priority: 1
estimated_minutes: 45
depends_on: ["S05-build-integration"]
modifies: ["web-ui/app/**/*.ts", "web-ui/app/**/*.tsx", "runner/src/index.js"]
executor: glm
---

## 目标

在 IDE 中加入 Test 按钮，根据链类型调用 `anchor test` (SVM) 或 `forge test` (EVM)，结果显示在 Reports 面板。

## 步骤

1. 添加 "Test" 按钮 (紧挨 Build 按钮)
2. 根据链类型调用:
   - SVM: `anchor test` → 解析 Anchor 测试输出 (Rust test format)
   - EVM: `forge test` → 解析 Forge 测试输出
3. 输出流式显示在终端面板
4. 测试完成后生成报告到 `reports/test.{chain}.{runner}.json`
5. Reports 面板显示:
   - 通过/失败计数 (✓ 12/12 或 ✗ 10/12)
   - 每个测试的名称 + 状态
   - 失败测试的错误信息
6. 状态栏更新: Tests 12/12 ✓

## 报告格式

```json
{
  "ok": true,
  "chain": "solana",
  "runner": "anchor",
  "action": "test",
  "summary": "12/12 tests passed",
  "details": {
    "passed": 12,
    "failed": 0,
    "tests": [
      {"name": "test_initialize", "status": "passed", "duration_ms": 120},
      {"name": "test_mint", "status": "passed", "duration_ms": 85}
    ]
  }
}
```

## 验收标准

- [ ] 点击 Test 按钮后终端显示测试输出
- [ ] SVM 调用 `anchor test`
- [ ] EVM 调用 `forge test`
- [ ] Reports 面板显示通过/失败计数
- [ ] 失败测试显示错误信息
- [ ] 生成 JSON 报告

## 不要做

- 不要实现 auto-repair (S12 做)
- 不要改 Build 逻辑
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
