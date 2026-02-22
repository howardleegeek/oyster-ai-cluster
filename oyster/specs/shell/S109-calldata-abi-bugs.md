---
task_id: S109-calldata-abi-bugs
project: shell
priority: 0
estimated_minutes: 30
depends_on: []
modifies: ["web-ui/app/utils/calldata.ts", "web-ui/app/utils/calldataCodec.js"]
executor: glm
---
## 目标
修复 ABI 编解码 10 个 bug (#28-#37)

## Bug 清单

### calldata.ts
28. ABI 字符串输入不处理 — 加 `typeof abiJson === 'string' ? JSON.parse(abiJson) : abiJson`
29. FunctionFragment 异常后 selector 为空 — fallback 返回明确错误信息
30. `data.slice(10)` 空数据崩溃 — 检查 `data.length >= 10` 再 slice
31. 元组解析丢失键名 — 用 Result.toObject() 保留命名属性
32. `normalizeAbi` 强制赋 type: 'function' — 跳过 constructor/receive/fallback
33. struct 类型拼接 selector 错误 — 用 ethers Fragment.from() 自动处理 tuple

### calldataCodec.js
34. KNOWN_FUNCTIONS 只有 transfer — 加 approve, transferFrom, balanceOf 等 ERC20 常用
35. 地址截断静默 — 验证长度 === 40，否则抛错
36. `BigInt(null)` 崩溃 — 加 null check: `args[1] ?? '0'`
37. 偏移量拼接冗余 — 简化为 `rest.substring(0, 64)`

## 验收标准
- [ ] 字符串 ABI 输入能正常解析
- [ ] 空 calldata '0x' 不崩溃
- [ ] struct/tuple 类型 selector 正确
- [ ] BigInt(null) 不报错
- [ ] TypeScript 编译通过

## 不要做
- 不改 UI 组件
- 不加新 ABI 功能
