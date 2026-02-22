---
task_id: S49-campaign-crud
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - backend/models.py
  - backend/routers/campaigns.py
  - backend/main.py
  - frontend/src/pages/Campaigns.tsx
  - frontend/src/App.tsx
executor: glm
---

## 目标
创建Campaign管理功能 - 营销战役单位

## 背景
v2 PRD: 营销战役(Campaign)是KPI/内容/人设的隔离管理单位

## 数据模型
新增 campaigns 表:
- id (uuid)
- brand_id (uuid, index)
- name
- objective_type: growth | conversion | launch
- start_date, end_date
- narrative_theme
- platforms (jsonb)
- kpi_targets (jsonb)
- status: draft | active | paused | completed

## API端点
- POST /api/v2/campaigns - 创建
- GET /api/v2/campaigns?brand_id= - 列表
- GET /api/v2/campaigns/{id} - 详情
- PATCH /api/v2/campaigns/{id} - 更新
- POST /api/v2/campaigns/{id}/pause
- POST /api/v2/campaigns/{id}/resume

## 前端页面
- /campaigns - 战役列表
- /campaigns/:id - 战役详情

## 验收标准
- [ ] campaigns表创建
- [ ] CRUD API可用
- [ ] 前端页面可访问
- [ ] 与Brand关联
