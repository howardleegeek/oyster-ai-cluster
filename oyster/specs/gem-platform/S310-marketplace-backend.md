---
task_id: S310-marketplace-backend
project: gem-platform
priority: 1
depends_on: []
modifies:
  - backend/app/db/market.py
  - backend/app/schemas/market.py
  - backend/app/services/market.py
  - backend/app/api/market.py
executor: glm
---

## 目标
实现 Marketplace 后端，支持挂单、撤单、2% 手续费、1% 版税

## 约束
- 使用现有 SQLAlchemy
- 不改前端
- 经济模型参数可配置

## 具体改动

### 1. Order 订单
- 挂单 (list)
- 撤单 (delist)
- 购买 (buy)
- 成交 (execute)

### 2. 手续费系统
- 2% 买家手续费 (配置可调)
- 1% 版税给原所有者 (配置可调)
- 收入统计 API

### 3. API Endpoints
- POST /api/market/orders (挂单)
- GET /api/market/orders (订单簿)
- DELETE /api/market/orders/{id} (撤单)
- POST /api/market/buy (购买)
- GET /api/market/history (交易历史)

### 4. 筛选功能
- 按品类筛选
- 按稀有度筛选
- 按价格范围筛选
- 按排序 (价格/时间)

### 5. 测试
- pytest tests/test_marketplace.py 全绿

## 验收标准
- [ ] 挂单成功
- [ ] 撤单成功
- [ ] 购买扣款正确
- [ ] 手续费/版税计算正确
- [ ] pytest 全绿
