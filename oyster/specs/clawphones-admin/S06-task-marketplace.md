---
task_id: S06-task-marketplace
project: clawphones-admin
priority: 1
depends_on: []
modifies:
  - ~/Downloads/clawphones-admin/src/app/tasks/
  - ~/Downloads/clawphones-admin/src/components/tasks/
executor: glm
---

## 目标
创建任务市场管理页面 (Sprint 14-15)

## 约束
- 使用 shadcn/ui
- 对接 /v1/tasks/* API

## 具体改动

### 1. 创建 Tasks 页面
创建 ~/Downloads/clawphones-admin/src/app/tasks/page.tsx:
- TaskList - 任务列表
- TaskDetail - 任务详情
- CreateTaskForm - 创建表单

### 2. 创建组件
创建 ~/Downloads/clawphones-admin/src/components/tasks/:
- TaskList.tsx
- TaskCard.tsx
- TaskForm.tsx
- EarningsChart.tsx

### 3. 功能
- GET /v1/tasks - 任务列表
- POST /v1/tasks - 创建任务
- GET /v1/tasks/{id} - 任务详情
- POST /v1/tasks/{id}/complete - 完成任务
- GET /v1/tasks/earnings - 收益统计

### 4. UI
- Card (任务卡片)
- Badge (状态: pending/active/completed)
- Progress (任务进度)
- Chart (收益图表)

## 验收标准
- [ ] /tasks 页面可访问
- [ ] 任务列表显示
- [ ] 可创建任务
- [ ] 收益统计图表

## 不要做
- 不修改 backend
