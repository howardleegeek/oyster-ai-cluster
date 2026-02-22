---
task_id: S03-token-management
project: clawphones-admin
priority: 1
depends_on: []
modifies:
  - ~/Downloads/clawphones-admin/src/app/tokens/
  - ~/Downloads/clawphones-admin/src/components/tokens/
executor: glm
---

## 目标
创建 Token 管理页面

## 约束
- 使用 shadcn/ui 组件
- 对接 /admin/tokens/* API

## 具体改动

### 1. 创建 Token 列表页面
创建 ~/Downloads/clawphones-admin/src/app/tokens/page.tsx:
- TokenTable - 表格显示所有 token
- 搜索/筛选功能
- 分页

### 2. 创建 Token 组件
创建 ~/Downloads/clawphones-admin/src/components/tokens/:
- TokenTable.tsx - Token 表格
- TokenForm.tsx - 创建/编辑表单
- TokenFilters.tsx - 筛选器

### 3. 功能
- GET /admin/tokens - 列表
- POST /admin/tokens/generate - 生成
- POST /admin/tokens/{id}/tier - 修改 tier
- POST /admin/tokens/{id}/disable - 禁用

### 4. UI 组件
使用 shadcn/ui:
- Table
- Button
- Dialog (创建弹窗)
- Select (tier 选择)
- Badge (状态标签)

## 验收标准
- [ ] /tokens 页面可访问
- [ ] 表格显示 token 列表
- [ ] 可生成新 token
- [ ] 可禁用 token

## 不要做
- 不修改 backend
