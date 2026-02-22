---
task_id: S106-stores-critical-bugs
project: shell
priority: 0
estimated_minutes: 35
depends_on: [S94-build-fix-critical]
modifies: ["web-ui/app/lib/stores/simulator.ts", "web-ui/app/lib/stores/livereload.ts", "web-ui/app/lib/stores/fuzz.ts", "web-ui/app/lib/stores/mcp.ts", "web-ui/app/lib/stores/test-runner.ts"]
executor: glm
---
## 目标
修复状态管理层 16 个 bug (#1-#16)

## Bug 清单

### simulator.ts
1. `_notify()` 监听器迭代 bug — `_listeners.slice().forEach(l => l(...))` 防止回调中取消订阅导致索引偏移
2. `simulateTransaction` 无超时 — 加 AbortSignal，30秒超时
3. 502/HTML 崩溃 — `resp.json()` 前检查 `resp.ok` 和 `content-type`
4. `JSON.stringify(payload)` 不支持 BigInt — 加 BigInt replacer: `(k,v) => typeof v === 'bigint' ? v.toString() : v`
5. 返回值不安全 — `json?.returnValue` 改为 `json?.simulationResult?.returnValue ?? null`

### livereload.ts
6. `require('nanostores')` 在现代打包器崩溃 — 改为 ESM `import`
7. 猴子补丁隐患 — 用 wrapper 函数替代直接修改 `.set`
8. 内存泄露 — `_enabledSubs` fallback 加 cleanup 返回值

### fuzz.ts
9. `fuzzStatus` 无类型约束 — 改为 `atom<'idle' | 'running' | 'done' | 'error'>('idle')`
10. 空数组越界 — 访问 `counterexamples[0]` 前检查 `length > 0`

### mcp.ts
11. 竞态条件 — `updateSettings` 加队列，最后一次 wins
12. localStorage 异步不同步 — API 调用前先写 localStorage（乐观更新）
13. SSR 水合错误 — `isBrowser` 判断移到 store 初始化外层
14. 抛错冗余 — 移除 `catch { throw }` 反模式

### test-runner.ts
15. 状态污染 — `startTestRun` 加锁防止连续点击
16. chainType 写死 — 改为 `string` 类型支持自定义链

## 验收标准
- [ ] simulator fetch 有 30s 超时
- [ ] BigInt 序列化不报错
- [ ] fuzzStatus 是 union type
- [ ] mcp updateSettings 无竞态
- [ ] TypeScript 编译通过

## 不要做
- 不改 UI 组件
- 不加新 store
- 不改 API 路由
