---
task_id: S200-marketplace-backend
project: gem-platform
priority: 1
depends_on: []
modifies:
  - backend/app/routers/market.py
  - backend/app/models/market.py
executor: glm
---

## 目标
实现市场交易后端 API：挂单、撤单、订单簿

## 约束
- 使用现有 SQLAlchemy 模型
- 不改前端代码
- 不加新依赖

## 具体改动
1. 创建 market.py router
2. 实现 POST /api/market/orders (挂单)
3. 实现 DELETE /api/market/orders/{id} (撤单)
4. 实现 GET /api/market/orders (订单簿)
5. 写单元测试

## 验收标准
- [ ] 挂单 API 返回 201
- [ ] 撤单 API 返回 200
- [ ] 订单簿返回正确数据
- [ ] pytest tests/market/ 全绿

## 不要做
- 不改前端
- 不实现支付
