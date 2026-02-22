---
task_id: S52-token-wizard
project: shell-vibe-ide
priority: 2
estimated_minutes: 25
depends_on: ["S04-prompt-templates", "S10-deploy"]
modifies: ["web-ui/app/components/workbench/TokenWizard.tsx", "templates/tokens/"]
executor: glm
---

## 目标

Token 标准向导：通过表单生成 ERC20/ERC721/ERC1155/SPL Token 合约代码。

## 步骤

1. `templates/tokens/` 下新建模板:
   - `ERC20.sol.template` (OpenZeppelin based)
   - `ERC721.sol.template`
   - `ERC1155.sol.template`
   - `SPLToken.rs.template` (Anchor)
2. `web-ui/app/components/workbench/TokenWizard.tsx`:
   - Step 1: 选择标准 (ERC20/721/1155/SPL)
   - Step 2: 配置参数:
     - ERC20: name, symbol, supply, mintable?, burnable?, pausable?
     - ERC721: name, symbol, maxSupply, baseURI, enumerable?
     - ERC1155: uri, pausable?
     - SPL: name, symbol, decimals, authority
   - Step 3: 预览生成的合约代码 (语法高亮)
   - Step 4: "Create Project" 按钮 → 写入编辑器
3. 代码生成逻辑:
   - 模板变量替换 ({{name}}, {{symbol}} 等)
   - OpenZeppelin import 路径正确
   - Anchor 的 SPL 模板包含 mint/transfer 指令

## 验收标准

- [ ] 4 种 token 标准可选
- [ ] 生成的代码可编译
- [ ] 参数在 UI 中可配置
- [ ] 预览时有语法高亮

## 不要做

- 不要实现自动部署 (用户手动 deploy)
- 不要实现自定义扩展 (基础功能够了)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
