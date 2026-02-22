---
task_id: S115-analytics-model
project: clawmarketing
priority: 2
depends_on: ["S106-brand-model"]
modifies: ["backend/models/models.py"]
executor: glm
---
## 目标
创建数据分析看板数据库模型

## 约束
- 使用 SQLAlchemy
- 写 pytest 测试

## 验收标准
- [ ] pytest tests/test_analytics_model.py 全绿
- [ ] Campaign 模型: id, brand_id, name, status, created_at
- [ ] CampaignMetrics 模型: id, campaign_id, impressions, clicks, engagement_rate, created_at

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
