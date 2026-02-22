---
task_id: S58-ai-natspec
project: shell-vibe-ide
priority: 3
estimated_minutes: 20
depends_on: ["S04-prompt-templates", "S34-ai-autocomplete"]
modifies: ["web-ui/app/components/workbench/NatSpecGenerator.tsx"]
executor: glm
---

## 目标

AI 文档生成器：一键为 Solidity 合约生成 NatSpec 注释，为 Anchor 程序生成 Rust doc 注释。

## 步骤

1. `web-ui/app/components/workbench/NatSpecGenerator.tsx`:
   - "Generate Docs" 按钮 (放在编辑器工具栏)
   - 点击后:
     - 读取当前文件内容
     - 检测语言 (Solidity → NatSpec, Rust → /// doc comments)
     - 调用 AI 生成文档注释
     - 在 Monaco 编辑器中 inline 插入注释
   - Solidity NatSpec 格式:
     - `@title`, `@author`, `@notice`, `@dev`
     - `@param`, `@return` 为每个函数
     - `@inheritdoc` 用于 override
   - Anchor Rust doc 格式:
     - `///` 模块级说明
     - `///` 每个 instruction handler
     - `///` 每个 account struct field
2. AI prompt 模板:
   - 系统 prompt: "你是 Solidity/Anchor 文档专家..."
   - 约束: 只生成注释，不修改代码
   - 输出格式: JSON [{line, comment}]

## 验收标准

- [ ] Solidity 文件生成 NatSpec
- [ ] Rust/Anchor 文件生成 doc comments
- [ ] 注释插入到正确位置
- [ ] 不修改原有代码

## 不要做

- 不要实现 README 生成 (只做 inline 注释)
- 不要实现批量处理 (一次一个文件)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
