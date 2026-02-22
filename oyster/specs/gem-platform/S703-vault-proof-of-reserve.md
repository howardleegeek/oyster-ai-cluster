---
task_id: S703-vault-proof-of-reserve
project: gem-platform
priority: 1
depends_on: []
modifies:
  - backend/app/api/vault.py
  - backend/app/models/rwa_asset.py
  - lumina/components/VaultPanel.tsx
executor: glm
---

## 目标
实现 Vault 证据链与 Proof-of-Reserve

## 功能需求

### 1. RWA Asset 证据链
每个实物资产必须有：
- cert_provider: PSA/BGS/CGC
- cert_number: 证书编号
- grade: 评级分数
- set: 系列
- card_no: 卡片编号
- images: 多角度高清图
- checkin_at: 入库时间
- checkin_operator: 操作员
- checkin_photos: 入库照片
- insured: 是否投保
- insurance_policy_no: 保单号
- insurance_amount: 保额

### 2. Proof-of-Reserve
- 定期生成库存 Merkle Root
- 上链或公开存档
- 用户可验证 NFT 是否在 PoR 中

## API
```
GET /api/vault/assets/{id}           - 资产详情
POST /api/vault/assets               - 创建资产
PUT /api/vault/assets/{id}           - 更新资产

GET /api/por/latest                 - 最新 PoR root
GET /api/por/verify/{nft_id}       - 验证 NFT 是否在 PoR
```

## 验收
- [ ] 证据链字段完整
- [ ] PoR 可生成
- [ ] 可验证
