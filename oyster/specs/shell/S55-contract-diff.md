---
task_id: S55-contract-diff
project: shell-vibe-ide
priority: 2
estimated_minutes: 25
depends_on: ["S36-git-integration"]
modifies: ["web-ui/app/components/workbench/ContractDiff.tsx", "web-ui/app/lib/stores/diff.ts"]
executor: glm
---

## 目标

合约对比工具：Side-by-side diff 视图比较两个合约版本，高亮 storage layout 变化和接口差异。

## 步骤

1. `web-ui/app/lib/stores/diff.ts`:
   - nanostores atom: `diffSource` (git-commit | file-upload | clipboard)
   - `diffResult`: { additions, deletions, storageChanges[], interfaceChanges[] }
2. `web-ui/app/components/workbench/ContractDiff.tsx`:
   - 左右分栏 Monaco diff editor (使用 `monaco.editor.createDiffEditor`)
   - 来源选择:
     - Git: 选择两个 commit 的同一文件
     - File: 上传/粘贴两个版本
   - 额外分析面板:
     - 函数签名变化 (added/removed/modified)
     - Event 签名变化
     - Storage variable 变化 (类型、slot 位置)
3. 差异分析:
   - 用正则解析 Solidity function/event/variable 定义
   - 对比两个版本的签名列表
   - Storage slot 变化标红警告

## 验收标准

- [ ] Monaco diff editor 正常工作
- [ ] Git commit 对比可用
- [ ] 函数签名变化检测正确
- [ ] Storage 变化有警告提示

## 不要做

- 不要实现完整的 AST 解析 (正则够用)
- 不要接入链上已部署代码对比 (S35 做)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
