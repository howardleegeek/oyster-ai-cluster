---
task_id: S113-sampler-utils-bugs
project: shell
priority: 1
estimated_minutes: 15
depends_on: []
modifies: ["web-ui/app/utils/sampler.ts"]
executor: glm
---
## 目标
修复 sampler 工具 3 个 bug (#63-#65)

## Bug 清单

63. Unmount 后幽灵回调 — 返回 `dispose()` 方法，调用时 clearTimeout + 标记 disposed
64. setTimeout 内错误不冒泡 — 用 try/catch 包裹 `fn.apply`，错误发送到全局 error handler
65. this 绑定丢失 — 创建时绑定 context，或改为箭头函数模式

## 验收标准
- [ ] sampler 返回 dispose 方法
- [ ] dispose 后不再执行回调
- [ ] 错误有明确处理路径
- [ ] TypeScript 编译通过

## 不要做
- 不改使用 sampler 的组件
