---
task_id: S52-publish-jobs
project: clawmarketing
priority: 4
depends_on: [S51-content-review]
modifies:
  - backend/models.py
  - backend/routers/publish.py
  - frontend/src/pages/Content.tsx
executor: glm
---

## 目标
创建 Publish Jobs - 内容发布管理

## 背景
v2 PRD: A路线(手动导出)优先

## 数据模型
- publish_jobs: 发布任务队列

## publish_jobs 表
- id (uuid)
- content_id (uuid)
- platform: twitter | discord | bluesky | linkedin | instagram | reddit
- scheduled_at (timestamp)
- status: pending | scheduled | published | failed
- platform_response (jsonb) - 平台返回
- created_at, updated_at

## API端点
- POST /api/v2/publish/jobs - 创建发布任务
- GET /api/v2/publish/jobs?content_id= - 查看发布任务
- POST /api/v2/publish/jobs/{id}/execute - 立即执行
- DELETE /api/v2/publish/jobs/{id} - 取消

## 前端
- Content 页面: 发布按钮 → 创建 publish_job
- 发布状态可视化

## 验收标准
- [ ] publish_jobs 表创建
- [ ] 可创建发布任务
- [ ] 可手动触发发布
- [ ] 记录平台返回
