---
task_id: S63-dependency-manager
project: shell-vibe-ide
priority: 2
estimated_minutes: 25
depends_on: ["S05-build-integration"]
modifies: ["web-ui/app/components/workbench/DependencyManager.tsx", "web-ui/app/lib/stores/deps.ts"]
executor: glm
---

## 目标

合约依赖管理器：管理 OpenZeppelin 版本、Foundry remappings、Anchor crate 版本，一键安装/升级。

## 步骤

1. `web-ui/app/lib/stores/deps.ts`:
   - nanostores atom: `dependencies` — [{name, version, source, installed}]
   - 解析来源:
     - EVM: foundry.toml remappings + lib/ 目录
     - SVM: Cargo.toml [dependencies]
2. `web-ui/app/components/workbench/DependencyManager.tsx`:
   - 列出当前项目的合约依赖
   - EVM 依赖:
     - OpenZeppelin contracts (显示版本, 一键 `forge install`)
     - Solmate / Solady 等常用库
     - 显示 remappings.txt 内容
   - SVM 依赖:
     - anchor-lang 版本
     - spl-token 版本
     - 显示 Cargo.toml 的 [dependencies]
   - 功能:
     - "Add Dependency" → 搜索 + 选择 → 生成安装命令
     - "Update" → 显示最新版本 + 更新命令
     - "Remove" → 删除命令
   - 命令在终端面板执行 (复用 S05 的终端集成)

## 验收标准

- [ ] 解析 foundry.toml 依赖
- [ ] 解析 Cargo.toml 依赖
- [ ] 安装/更新命令正确
- [ ] 列表正确显示

## 不要做

- 不要实现 npm 依赖管理 (只管合约依赖)
- 不要自动安装 (展示命令, 用户确认执行)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
