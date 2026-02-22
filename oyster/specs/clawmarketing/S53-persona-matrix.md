---
task_id: S53-persona-matrix
project: clawmarketing
priority: 5
depends_on: [S50-strategy-api]
modifies:
  - backend/models.py
  - backend/routers/personas.py
  - frontend/src/pages/Personas.tsx
executor: glm
---

## 目标
创建 Persona Matrix - 参数化人设卡片

## 背景
v2 PRD: Persona 从文本设定 → 资产卡片 + 调参面板

## 数据模型
- personas 表增加:
  - campaign_id (uuid)
  - persona_type: authority | emotional | educational | engagement
  - parameters (jsonb): emotion, voice, aggression 等
  - content_pillars (jsonb)
  - risk_level (low | medium | high)

## API端点
- GET /api/v2/personas?campaign_id= - 按战役获取
- POST /api/v2/personas - 创建人设
- POST /api/v2/personas/{id}/clone - 克隆人设
- PATCH /api/v2/personas/{id}/parameters - 更新参数

## 前端
- Persona Matrix 页面: 4类卡片视图
- 每个卡片显示:
  - 绑定账号
  - 平台标签
  - 3个 content pillars
  - 参数滑杆
  - 本周 KPI mini sparkline

## 验收标准
- [ ] personas 表有 campaign_id 和 parameters
- [ ] 可创建/克隆人设
- [ ] 前端 Persona Matrix 视图
