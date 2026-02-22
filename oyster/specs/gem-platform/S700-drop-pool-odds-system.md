---
task_id: S700-drop-pool-odds-system
project: gem-platform
priority: 1
depends_on: []
modifies:
  - backend/app/db/drop.py
  - backend/app/schemas/drop.py
  - backend/app/api/drop.py
  - backend/app/models/drop.py
executor: glm
---

## 目标
实现 Drop/Pool/OddsVersion 体系，管理 Pack 发行批次

## 功能需求

### 1. Drop (发行批次)
- drop_id: 唯一标识
- pack_id: 关联的 Pack
- pool_id: 关联的卡池
- odds_version: 概率版本
- start_time: 开始时间
- end_time: 结束时间
- total_supply: 总供应量
- remaining: 剩余数量
- status: draft/active/ended

### 2. Pool (卡池)
- pool_id: 唯一标识
- name: 池名称
- cards: 卡片列表 (card_id, rarity, quantity)
- rarity_distribution: 稀有度分布
- hash: 卡池内容哈希 (用于验证)

### 3. OddsVersion (概率版本)
- version: 版本号
- pack_id: Pack ID
- rarity_weights: 稀有度权重
- created_at: 创建时间
- locked: 是否锁定 (锁定后不可修改)

## API Endpoints

```
GET  /api/drops              - 列出 Drop
POST /api/drops              - 创建 Drop
GET  /api/drops/{id}        - Drop 详情
PUT  /api/drops/{id}/end    - 结束 Drop

GET  /api/pools             - 列出 Pool
POST /api/pools             - 创建 Pool
GET  /api/pools/{id}        - Pool 详情

GET  /api/odds/versions     - 概率版本列表
POST /api/odds/versions     - 创建概率版本
```

## 约束
- 使用现有 SQLAlchemy + FastAPI
- 不改其他模块

## 验收
- [ ] Drop CRUD 完整
- [ ] Pool 管理完整
- [ ] OddsVersion 版本锁定
- [ ] API 可用
