---
task_id: S912-event-tracking
project: gem-platform
priority: 1
depends_on: []
modifies:
  - backend/app/services/event_tracker.py
  - backend/app/api/pack.py
  - backend/app/api/market.py
  - backend/app/api/buyback.py
executor: glm
---

## Week 1 - 事件追踪系统

## 目标
关键事件埋点

## 事件
- purchase_pack
- open_pack
- mint_nft
- list (market)
- buy (market)
- buyback_quote
- buyback_execute
- redeem_create
- redeem_ship

## 存储
- event_logs 表
- 事件ID、用户ID、事件类型、详情、时间

## API
GET /api/admin/events - 查询事件日志

## 验收
- [ ] 关键事件被记录
- [ ] 可查询
