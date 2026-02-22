---
task_id: S702-buyback-system
project: gem-platform
priority: 1
depends_on: []
modifies:
  - backend/app/api/buyback.py
  - backend/app/db/buyback.py
  - backend/app/models/buyback.py
  - backend/app/schemas/buyback.py
  - lumina/services/buybackApi.ts
executor: glm
---

## 目标
实现完整的回购系统

## 功能需求

### 1. 回购政策 (BuybackPolicy)
- price_type: pack_price / nft_floor / platform_index
- window_days: 购买后多少天可回购
- cooldown_hours: 购买后冷却时间
- daily_limit_per_user: 每日每用户限额
- total_daily_limit: 每日总限额
- buyback_rate: 回购比例 (0.85 / 0.90)
- applicable_packs: 适用 Pack 列表

### 2. 回购准备金 (BuybackReserve)
- total_pool: 总资金池
- available: 可用金额
- coverage_rate: 覆盖率

### 3. 回购流程
- 报价 (先报价再确认)
- 申请
- 审核
- 打款

## API
```
GET  /api/buyback/policy     - 当前政策
GET  /api/buyback/reserve    - 准备金状态
POST /api/buyback/quote      - 报价
POST /api/buyback/request    - 申请回购
GET  /api/buyback/requests  - 列表
```

## 验收
- [ ] 政策可配置
- [ ] 报价机制
- [ ] 准备金展示
