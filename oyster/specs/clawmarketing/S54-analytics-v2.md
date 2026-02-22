---
task_id: S54-analytics-v2
project: clawmarketing
priority: 6
depends_on: [S51-content-review]
modifies:
  - backend/routers/analytics.py
  - frontend/src/pages/Analytics.tsx
executor: glm
---

## 目标
升级 Analytics - 决策 + 建议

## 背景
v2 PRD: Analytics 必须回答 4 个问题

## Analytics v2 必须有

### 视图
1. **Campaign Overview**: KPI, 趋势, ROI
2. **Persona Compare**: 同战役下 persona 横向对比
3. **Hook Library**: Top hooks, 按模板聚类
4. **Risk Metrics**: 风险触发率, 重复率, 敏感词命中

### 输出
- **Optimizer 建议**: persona 参数 delta
- **是否建议 clone persona 做 A/B**

## API端点
- GET /api/v2/analytics/campaign/{id} - 战役分析
- GET /api/v2/analytics/persona/compare?campaign_id= - Persona 对比
- GET /api/v2/analytics/hooks - Hook 效果排行
- GET /api/v2/analytics/risk - 风险统计
- GET /api/v2/analytics/optimizer - 优化建议

## 验收标准
- [ ] 4个视图可访问
- [ ] Optimizer 给出建议
