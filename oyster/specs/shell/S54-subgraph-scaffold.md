---
task_id: S54-subgraph-scaffold
project: shell-vibe-ide
priority: 2
estimated_minutes: 30
depends_on: ["S04-prompt-templates", "S40-abi-manager"]
modifies: ["web-ui/app/components/workbench/SubgraphWizard.tsx", "templates/subgraph/"]
executor: glm
---

## 目标

Subgraph 脚手架：从合约 ABI 自动生成 The Graph subgraph 代码 (schema.graphql + mapping.ts + subgraph.yaml)。

## 步骤

1. `templates/subgraph/` 下新建模板:
   - `schema.graphql.template` — 从 ABI events 生成 entity 定义
   - `mapping.ts.template` — 事件处理器模板
   - `subgraph.yaml.template` — manifest 模板
2. `web-ui/app/components/workbench/SubgraphWizard.tsx`:
   - Step 1: 选择已部署合约 (或粘贴 ABI JSON)
   - Step 2: 选择要索引的 events (checkbox 列表)
   - Step 3: 预览生成的 schema + mapping + manifest
   - Step 4: "Create Subgraph Project" → 写入编辑器
3. 代码生成逻辑:
   - 解析 ABI 的 event 定义 → GraphQL entity
   - event 参数 → entity fields (address→Bytes, uint256→BigInt)
   - 生成 mapping handler 函数骨架
   - subgraph.yaml 填入合约地址 + startBlock

## 验收标准

- [ ] 从 ABI 生成完整 subgraph 项目
- [ ] schema.graphql 类型正确
- [ ] mapping.ts 编译通过 (AssemblyScript)
- [ ] subgraph.yaml 格式正确

## 不要做

- 不要实现 Graph Node 部署 (用户自己跑 `graph deploy`)
- 不要支持 SVM (The Graph 目前只支持 EVM)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
