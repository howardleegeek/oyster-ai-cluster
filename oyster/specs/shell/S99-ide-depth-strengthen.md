---
task_id: S99-ide-depth-strengthen
project: shell
priority: 2
estimated_minutes: 40
depends_on: [S94-build-fix-critical]
modifies: ["web-ui/app/components/workbench/", "web-ui/app/components/editor/"]
executor: glm
---
## 目标
加强 Shell 独有的 IDE 深度优势 — Noah 做不到的专业开发者体验

## 约束
- 基于现有 CodeMirror editor 扩展
- 不换编辑器引擎
- Solidity + TypeScript 双语言支持

## 实现
1. Solidity 智能提示：自动补全 OpenZeppelin 常用合约接口
2. 内联错误标注：编译错误直接在编辑器里标红 + hover 显示详情
3. Gas 估算面板：编辑合约时实时显示各函数预估 gas cost
4. 合约关系图：可视化 import 依赖 + 继承关系 (简单的 SVG 树)
5. Terminal 增强：支持 `forge test --gas-report` 输出格式化显示

## 验收标准
- [ ] Solidity 自动补全在 CodeMirror 里可用
- [ ] 编译错误内联显示
- [ ] Gas 面板组件存在且有 mock 数据
- [ ] 合约关系图组件存在
- [ ] TypeScript 编译通过

## 不要做
- 不换 CodeMirror 为 Monaco
- 不做 LSP server
- 不改 Terminal 核心逻辑
