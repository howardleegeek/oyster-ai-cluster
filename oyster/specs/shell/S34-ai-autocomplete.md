---
task_id: S34-ai-autocomplete
project: shell-vibe-ide
priority: 2
estimated_minutes: 45
depends_on: ["S03-dual-syntax-support"]
modifies: ["web-ui/app/components/editor/ai-autocomplete.ts", "web-ui/app/lib/ai/inline-completion.ts", "web-ui/app/lib/ai/web3-context.ts"]
executor: glm
---

## 目标

在编辑器中添加 AI 代码自动补全 (类似 Copilot/Continue)。

## 开源方案

- **Continue** (continuedev/continue): Tab 自动补全引擎
- 复用 bolt.diy 的 AI 模型连接

## 步骤

1. 实现 inline completion:
   - 用户停止输入 500ms 后触发
   - AI 基于当前文件上下文生成补全
   - 灰色文字预览 (ghost text)
   - Tab 接受 / Esc 取消
2. Web3 上下文增强:
   - 自动注入链信息 (当前选择的链)
   - Solidity: OpenZeppelin 模式补全
   - Rust/Anchor: Anchor 宏和账户结构补全
3. 多行补全:
   - 整个函数生成
   - 测试用例生成
4. 补全质量优化:
   - 文件内 context (当前文件)
   - 项目内 context (import 的文件)
   - Web3 知识 (常见模式)

## 验收标准

- [ ] 停止输入后显示灰色补全建议
- [ ] Tab 接受补全
- [ ] Solidity 和 Rust 都能补全
- [ ] 补全包含 Web3 上下文
- [ ] 不影响编辑器性能

## 不要做

- 不要自己训练模型 (用现有 API)
- 不要实现 LSP server (用 AI 补全替代)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
