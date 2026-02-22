---
task_id: S300-pack-system-backend
project: gem-platform
priority: 1
depends_on: []
modifies:
  - backend/app/db/pack.py
  - backend/app/schemas/pack.py
  - backend/app/services/pack_engine.py
  - backend/app/api/pack.py
executor: glm
---

## 目标
实现完整的 Pack 盲盒系统后端，支持多品类、分级、概率、Buyback

## 约束
- 使用现有 SQLAlchemy + FastAPI
- 不改前端代码
- 不硬编码 secrets 到代码

## 具体改动

### 1. Pack 品类支持
扩展 pack categories 支持:
- POKEMON, BASEBALL, BASKETBALL, FOOTBALL, ONE_PIECE, YU_GI_OH

### 2. Pack 等级
- STARTER ($25)
- ROOKIE ($25)
- PRO ($100)
- ELITE ($50)
- LEGEND ($250)
- PLATINUM ($500)
- SEALED ($100)

### 3. Buyback 系统
- 85% buyback (标准)
- 90% buyback (BOOST 活动款)
- 计算公式和 API

### 4. 概率系统
- 每个 Pack 类型的概率配置表
- N/VV/SSR/SSR+/XR/Legendary 等级分布
- 区块链可验证随机数

### 5. API Endpoints
- GET /api/packs - 列出所有 Pack 类型
- GET /api/packs/{id} - Pack 详情
- POST /api/packs/purchase - 购买 Pack
- POST /api/packs/open - 开盒
- POST /api/packs/buyback - Buyback 申请

### 6. 测试
- pytest tests/test_pack_engine.py 全部通过

## 验收标准
- [ ] 列出 7+ Pack 类型
- [ ] 购买返回 NFT 信息
- [ ] 开盒揭示稀有度正确
- [ ] Buyback 计算正确 (85%/90%)
- [ ] pytest 全绿
