---
task_id: S67-anchor-idl
project: shell-vibe-ide
priority: 2
estimated_minutes: 20
depends_on: ["S05-build-integration", "S40-abi-manager"]
modifies: ["web-ui/app/components/workbench/AnchorIdlViewer.tsx"]
executor: glm
---

## 目标

Anchor IDL 查看器：解析和展示 Anchor 程序的 IDL JSON，可视化 instructions、accounts、types。

## 步骤

1. `web-ui/app/components/workbench/AnchorIdlViewer.tsx`:
   - 读取 `target/idl/*.json` 编译产物
   - 三个 Tab:
     - Instructions: 列出所有 instruction + 参数 + accounts
     - Accounts: 列出所有 account struct + fields
     - Types: 列出自定义类型 + enums
   - 每个 instruction 显示:
     - 名称
     - args 列表 (name + type)
     - accounts 列表 (name + isMut + isSigner)
   - 支持:
     - 从文件加载 IDL JSON
     - 从链上拉取 IDL (anchor idl fetch <program-id>)
     - 搜索/过滤
   - 与 S21 合约交互面板联动: 选择 instruction → 跳转到交互面板

## 验收标准

- [ ] 正确解析 Anchor IDL JSON
- [ ] Instructions/Accounts/Types 三 tab 可切换
- [ ] 搜索过滤可用
- [ ] 文件加载和链上拉取可用

## 不要做

- 不要实现 IDL 编辑 (只读)
- 不要生成客户端代码 (用 Anchor 自带的)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
