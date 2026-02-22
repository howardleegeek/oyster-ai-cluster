---
task_id: S112-test-runner-bugs
project: shell
priority: 0
estimated_minutes: 25
depends_on: []
modifies: ["web-ui/app/lib/web3/test-runner.ts"]
executor: glm
---
## 目标
修复 Test Runner 6 个 bug (#57-#62)

## Bug 清单

57. stderr 无视 — 合并 stderr 到解析输出，或单独检查 stderr 报编译错误
58. skipped 测试漏统计 — `total = passed + failed + skipped`
59. 同名用例擦除 — 用 `${suite}:${test.name}:${test.status}` 作为去重 key
60. `\r` 回车符处理 — 加 `.replace(/\r(?!\n)/g, '\n')` 处理实时进度渲染残留
61. 逐行 JSON.parse try/catch 性能灾难 — 先用正则 `/^\s*[\[{]/ ` 预筛，再 parse
62. Anchor 日志时间戳干扰匹配 — 正则允许前缀 timestamp `\[\d+:\d+\]`

## 验收标准
- [ ] stderr 错误能被检测到
- [ ] total = passed + failed + skipped
- [ ] 同 suite 不同名测试不被去重
- [ ] `\r` 不导致解析失败
- [ ] TypeScript 编译通过

## 不要做
- 不改 test runner 核心执行逻辑
- 不加新链类型支持
