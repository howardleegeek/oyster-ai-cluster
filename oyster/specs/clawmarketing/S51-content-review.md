---
task_id: S51-content-review
project: clawmarketing
priority: 3
depends_on: [S49-campaign-crud]
modifies:
  - backend/models.py
  - backend/routers/content.py
  - frontend/src/pages/Content.tsx
executor: glm
---

## 目标
创建 Content Kanban 和 Review Queue

## 背景
v2 PRD: 内容管理状态机 + 审核流程

## 数据模型
新增/修改表:
- content_items: 添加 campaign_id, status, review_status
- content_variants: A/B测试内容变体
- review_tasks: 审核任务队列

## Content Status Machine
- draft → in_review → approved → scheduled → published → failed → archived

## API端点
- GET /api/v2/content?campaign_id= - 内容列表
- POST /api/v2/content - 创建内容
- POST /api/v2/content/{id}/submit-review - 提交审核
- POST /api/v2/content/{id}/approve - 批准
- POST /api/v2/content/{id}/reject - 拒绝

## 前端
- Content 页面: Kanban 视图（按 status 分列）
- Review Queue: 待审核内容列表

## 验收标准
- [ ] content_items 表有 campaign_id 和 status
- [ ] content_variants 表支持 A/B 测试
- [ ] review_tasks 表记录审核历史
- [ ] Content 页面 Kanban 可视化
- [ ] 审核流程可工作
