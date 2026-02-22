---
task_id: S55-scheduler-queue
project: clawmarketing
priority: 7
depends_on: [S52-publish-jobs]
modifies:
  - backend/routers/scheduler.py
  - frontend/src/pages/Scheduler.tsx
executor: glm
---

## 目标
创建 Scheduler Queue - 轻量排期

## 背景
v2 PRD: MVP 先做队列，不做复杂 calendar

## 数据模型
- scheduled_posts: 排期队列

## scheduled_posts 表
- id (uuid)
- content_id (uuid)
- persona_id (uuid)
- platform
- scheduled_at (timestamp)
- status: pending | published | failed | cancelled
- created_at

## API端点
- POST /api/v2/scheduler - 添加排期
- GET /api/v2/scheduler?status=pending - 查看队列
- DELETE /api/v2/scheduler/{id} - 取消
- POST /api/v2/scheduler/{id}/execute - 立即执行

## 前端
- Scheduler 页面: 时间排序的 Scheduled items
- 规则提示: 发帖频率上限, persona 错峰
- 手动导出包: 到点提醒复制发布

## 验收标准
- [ ] 可添加排期
- [ ] 可取消
- [ ] 队列可视化
