---
task_id: S704-marketplace-transparency
project: gem-platform
priority: 1
depends_on: []
modifies:
  - backend/app/api/market.py
  - lumina/components/MarketplaceUpdates.tsx
executor: glm
---

## 目标
升级 Marketplace 资产详情透明化

## 功能需求

### 1. 资产详情页必须展示
- NFT 信息 (链上)
- 实物信息 (vault)
- 是否可兑付
- 兑付费用预估
- 预计发货时效

### 2. 市场数据透明
- 最近成交价
- 7D/30D 成交量
- 地板价

### 3. 新增 API
```
GET /api/market/assets/{id} - 资产详情 (NFT + 实物 + 兑付)

GET /api/market/stats      - 市场统计
  - floor_price
  - volume_7d
  - volume_30d
  - sales_count
```

## 验收
- [ ] 资产详情页完整
- [ ] 市场统计可用
