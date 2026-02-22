---
task_id: S301-pack-opening-frontend
project: gem-platform
priority: 1
depends_on:
  - S300-pack-system-backend
modifies:
  - lumina/components/PackStoreView.tsx
  - lumina/components/PackOpening.tsx
  - lumina/services/packApi.ts
executor: glm
---

## 目标
实现 Pack 开盒前端，炫酷揭示效果

## 约束
- 使用现有 Vite + React 架构
- 不改后端 API
- 动画流畅，有 loading 状态

## 具体改动

### 1. Pack Store 页面
- 展示所有 Pack 类型 (按品类分组)
- Pack 卡片显示: 图片、名称、价格、Buyback 比例
- 筛选: 品类、价格、Buyback
- 数量选择 + 加入购物车

### 2. 开盒流程
- 点击 "Open" 触发购买 + 开盒
- 开盒动画 (至少 3 秒)
- 揭示稀有度 (N/VV/SSR/SSR+/XR/Legendary)
- 揭示卡片图片
- 揭示 NFT 信息

### 3. 揭示效果
- 卡片翻转动画
- 稀有度发光效果
- 音效 (可选)
- 分享按钮 (Twitter/X)

### 4. 购买后操作
- Hold (持有)
- Sell (挂单 Marketplace)
- Buyback (卖回给平台)
- Redeem (兑换实物)

## 验收标准
- [ ] Pack Store 显示 7+ 类型
- [ ] 开盒动画流畅
- [ ] 稀有度正确显示
- [ ] 4 个操作按钮可用
