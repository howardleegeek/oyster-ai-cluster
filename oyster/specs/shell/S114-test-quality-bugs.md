---
task_id: S114-test-quality-bugs
project: shell
priority: 1
estimated_minutes: 20
depends_on: []
modifies: ["web-ui/app/billing/__tests__/billing.test.ts", "web-ui/app/components/workbench/__tests__/ContractSizeBar.test.tsx"]
executor: glm
---
## 目标
修复测试质量 + 通用规范 9 个 bug (#66-#74)

## Bug 清单

66. billing.test.ts 全局变量不隔离 — 加 beforeEach reset
67. ContractSizeBar.test.js 用 CJS require — 改为 ESM import
68. contractSize 颜色梯度边界未测试 — 加 24.576 KB 边界测试
69. ensResolver avatar XSS — URL() 校验 + 只允许 https
71. generateId 碰撞 — 改用 crypto.randomUUID()
72. simulateTransaction Content-Type 硬编码 — 提取为配置项
73. setSimulationResult 无 diff 通知泛滥 — 加 deep-equal 检查再 notify
74. `result = json as any` 感染 — 定义 SimulationApiResponse interface

## 验收标准
- [ ] 测试文件全用 ESM import
- [ ] billing test 有 beforeEach reset
- [ ] generateId 用 crypto API
- [ ] TypeScript 编译通过

## 不要做
- 不重写测试框架
- 不加新测试文件
