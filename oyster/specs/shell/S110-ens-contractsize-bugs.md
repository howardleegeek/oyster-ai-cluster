---
task_id: S110-ens-contractsize-bugs
project: shell
priority: 1
estimated_minutes: 20
depends_on: []
modifies: ["web-ui/app/utils/ensResolver.ts", "web-ui/app/utils/contractSize.js"]
executor: glm
---
## 目标
修复 ENS + ContractSize 工具 10 个 bug (#38-#46, #70)

## Bug 清单

### ensResolver.ts
38. provider 非空检查缺失 — 加 `if (!provider) throw new Error('Provider required')`
39. SNS 动态 import 无缓存 — 用模块级变量缓存 import 结果
40. 多字段解析串行阻塞 — 改为 `Promise.all([getText('url'), getText('email'), ...])`
41. `@ts-ignore` 掩盖错误 — 移除 ts-ignore，正确处理 string throw
42. Bonfida API 版本不兼容 — 加 try/catch + 版本降级 fallback
70. avatar URL XSS — 用 `new URL()` 校验，只允许 https 协议

### contractSize.js
43. 奇数长度 hex 计算精度错 — `Math.ceil(clean.length / 2)`
44. 非 string 输入静默降级 — 改为 throw TypeError
45. EVM 阈值不准 — `EVM_YELLOW_MAX = 24576` (24.576 KB, EIP-170)
46. toFixed + replace 冗余 — 直接 `(bytes / 1024).toFixed(1)` 返回数字

## 验收标准
- [ ] ENS 解析多字段并行
- [ ] SNS import 有缓存
- [ ] contractSize 非 string 输入抛错
- [ ] TypeScript 编译通过

## 不要做
- 不加新 ENS 功能
- 不改 UI
