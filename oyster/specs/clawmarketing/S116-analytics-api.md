---
task_id: S116-analytics-api
project: clawmarketing
priority: 2
depends_on: ["S115-analytics-model"]
modifies: ["backend/api/analytics.py", "backend/main.py"]
executor: glm
---
## 目标
实现数据分析看板 API 端点

## 约束
- 使用 FastAPI 路由
- 写 pytest 测试

## 验收标准
- [ ] pytest tests/test_analytics_api.py 全绿
- [ ] GET /api/v1/analytics/summary — 全局数据摘要
- [ ] GET /api/v1/analytics/campaigns/{id} — 单个活动详情
- [ ] GET /api/v1/analytics/brands/{id}/performance — 品牌表现

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
