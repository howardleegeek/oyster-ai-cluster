---
task_id: S59-content-kanban
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - frontend/src/pages/Content.tsx
---

## 目标
Content 页面完整功能连接

## 具体改动
- 连接 /api/v2/content/ 获取真实数据
- 实现拖拽排序
- 实现状态变更 (draft → review → approved → published)
- 实现内容详情弹窗
- 实现发布按钮 → /api/v2/content/{id}/publish

## 验收标准
- [ ] Kanban 显示真实内容
- [ ] 可以拖拽变更状态
- [ ] 发布功能正常
