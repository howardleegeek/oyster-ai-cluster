---
task_id: S910-trust-center-drop-page
project: gem-platform
priority: 1
depends_on: []
modifies:
  - lumina/components/PackStoreView.tsx
  - backend/app/api/drop.py
executor: glm
---

## Week 1 - Trust Center: Drop 详情页

## 目标
标准化展示 Drop 信息和验证机制

## 功能
1. Drop 详情页展示:
   - Drop / Pool / OddsVersion
   - 概率披露 (稀有度分布)
   - Merkle Root
   - "How to verify" 三步指引

2. 可复制字段:
   - Pool ID
   - Odds Version
   - Merkle Root

## 验收
- [ ] Drop 详情完整展示
- [ ] 验证字段可复制
