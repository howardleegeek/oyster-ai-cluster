---
task_id: S04-user-management
project: clawphones-admin
priority: 1
depends_on: []
modifies:
  - ~/Downloads/clawphones-admin/src/app/users/
  - ~/Downloads/clawphones-admin/src/components/users/
executor: glm
---

## 目标
创建用户管理页面

## 约束
- 使用 shadcn/ui 组件
- 对接 /v1/user/* API

##具体改动

### 1. 创建 Users 页面
创建 ~/Downloads/clawphones-admin/src/app/users/page.tsx:
- UserTable - 用户列表
- 搜索/筛选 (按 email, tier, status)
- 分页

### 2. 创建 Users 组件
创建 ~/Downloads/clawphones-admin/src/components/users/:
- UserTable.tsx
- UserDetail.tsx
- UserFilters.tsx

### 3. 功能
- GET /v1/users - 用户列表
- GET /v1/users/{id} - 用户详情
- PUT /v1/users/{id} - 修改用户
- DELETE /v1/users/{id} - 删除用户

### 4. UI
- Table, Button, Dialog
- Badge (tier: free/pro/max)
- Avatar (用户头像)

## 验收标准
- [ ] /users 页面可访问
- [ ] 用户列表显示
- [ ] 可查看用户详情
- [ ] 可搜索/筛选

## 不要做
- 不修改 backend
