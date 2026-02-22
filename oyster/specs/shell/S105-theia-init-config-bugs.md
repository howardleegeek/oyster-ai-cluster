---
task_id: S105-theia-init-config-bugs
project: shell
priority: 1
estimated_minutes: 25
depends_on: []
modifies: ["desktop/theia-extension/", "init.sh", "desktop/start.sh", "desktop/package.json"]
executor: glm
---
## 目标
修复 Theia Extension + Init Script + Desktop Config 的 11 个 bug (#22-#27, #40-#43, #49-#50)

## Bug 清单

### Critical
22. **detectProjectType 硬编码 'evm'** — 修复: 检查 Anchor.toml → solana, foundry.toml → evm
23. **runDeploy 空函数** — 修复: 调用 runner 的 deploy action
24. **listReports 返回空数组** — 修复: 读 reports/ 目录
25. **readReport 返回空对象** — 修复: 读具体 report JSON 文件
26. **直接修改 state** — 修复: 用 setState 或 Theia binding
27. **缺少 React import** — 修复: 加 import React

### High
49. **init.sh 删除 .opencode/** — 丢失所有 Web3 能力。修复: 不删 .opencode/ 或在删除前备份
50. **init.sh 用 /tmp/shell-keep 无唯一性** — 修复: 用 mktemp -d

### Medium
40. **start.sh 不验证目录** — 修复: 加 cd 前检查
41. **start.sh 无 trap cleanup** — 修复: 加 trap "cleanup" EXIT
42. **package.json 缺 vite 依赖** — 修复: 加 vite 到 devDependencies
43. **tsconfig 冲突** — 修复: 统一两个 tsconfig 的 target/module

## 验收标准
- [ ] detectProjectType 能区分 evm/solana
- [ ] init.sh 不删除 .opencode/ 和 tests/
- [ ] start.sh 有 trap cleanup
- [ ] TypeScript 编译通过

## 不要做
- 不重写 Theia 架构
- 不动 web-ui
- 不加新功能
