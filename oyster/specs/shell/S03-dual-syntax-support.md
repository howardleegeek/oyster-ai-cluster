---
task_id: S03-dual-syntax-support
project: shell-vibe-ide
priority: 1
estimated_minutes: 30
depends_on: ["S01-fork-bolt-diy"]
modifies: ["web-ui/app/**/*.ts", "web-ui/app/**/*.tsx"]
executor: glm
---

## 目标

在 Monaco 编辑器中加入 Rust 和 Solidity 语法高亮支持。

## 背景

Shell 支持双链：SVM (Rust/Anchor) + EVM (Solidity)。bolt.diy 的 Monaco 编辑器默认不支持 Rust 和 Solidity。

## 步骤

1. 找到 bolt.diy 中 Monaco 编辑器的配置/初始化代码
2. 注册 Rust 语言:
   - 文件后缀: `.rs`
   - 使用 Monaco 内置的 Rust tokenizer (如果有)，否则用 `monaco-editor/esm/vs/basic-languages/rust/rust`
3. 注册 Solidity 语言:
   - 文件后缀: `.sol`
   - 需要自定义 tokenizer (Solidity 不是 Monaco 内置语言)
   - 参考: https://github.com/nickvdyck/monaco-solidity 或内联定义
   - 关键词: `pragma`, `contract`, `function`, `mapping`, `uint256`, `address`, `modifier`, `event`, `emit`, `require`, `payable`, `view`, `pure`, `external`, `internal`, `public`, `private`
4. 注册 TOML 语言 (Anchor.toml, Cargo.toml):
   - 文件后缀: `.toml`
   - 使用 Monaco 的 TOML 支持或简单 tokenizer
5. 设置默认主题色为赛博朋克 (token 颜色):
   - 关键词: `#b84dff` (紫)
   - 字符串: `#00ff88` (绿)
   - 注释: `#666666`
   - 类型: `#4dc9f6` (蓝)
   - 数字: `#ffaa00` (橙)

## 约束

- 只改 Monaco 配置
- 不要引入 LSP server (太重，后续做)
- 尽量用 Monaco 内置能力，少加依赖

## 验收标准

- [ ] `.rs` 文件有 Rust 语法高亮
- [ ] `.sol` 文件有 Solidity 语法高亮
- [ ] `.toml` 文件有基本高亮
- [ ] token 颜色符合赛博朋克主题
- [ ] 不影响其他语言 (JS/TS/JSON 等) 的高亮

## 不要做

- 不要加 LSP
- 不要加自动补全 (后续做)
- 不要改编辑器布局
- 不要碰 desktop/ 和 runner/
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
