# GEM S1 Fix Batch 2 — BLOCKER + 前后端对齐

## Task 7: Fix pack_engine.py typo + missing attribute + test import
**文件**: `backend/app/services/pack_engine.py`, `backend/tests/test_pack_engine.py`
**问题**:
1. Line 11: `PackPackOpeningStatus` 拼写错误 → 改为 `PackOpeningStatus`
2. Line 210: `acquired_at=now` → UserVault model 没有 acquired_at 字段，删掉这行（model 有 created_at 自动填充）
3. tests/test_pack_engine.py line 23: `from app.main import app` → 改为 `from app.app import app`
**约束**: 只改这 2 个文件

## Task 8: Fix market service missing relationship
**文件**: `backend/app/models/pack.py`, `backend/app/services/market.py`
**问题**: services/market.py line 145 用 `vault_item.opening` 但 UserVault model 没定义这个 relationship
**修复方案 (二选一)**:
- 方案 A (推荐): 在 services/market.py 中改为用 opening_id 查询: `opening = db.get(models.PackOpening, vault_item.opening_id)`
- 方案 B: 在 models/pack.py 的 UserVault class 中添加 `opening = relationship("PackOpening", foreign_keys=[opening_id])`
**约束**: 选一个方案实现。先读 models/pack.py 看 UserVault 的完整定义再决定

## Task 9: 枚举统一
**文件**: `backend/app/models/enums.py`, `backend/app/models/pack.py`, 以及所有引用枚举的 service/test 文件
**问题**: Rarity, PackStatus, PackOpeningStatus, UserVaultStatus 在 enums.py 和 pack.py 中都有定义，值还不一样
**修复**:
1. 先读 enums.py 和 pack.py，列出所有重复枚举和它们的值差异
2. 以 pack.py 中的定义为准（因为 model Column 类型引用 pack.py 的枚举）
3. 删除 enums.py 中的重复枚举，或让 enums.py 中的重复枚举 re-export pack.py 的
4. 更新所有 `from app.models.enums import` 的引用，确保导入正确的枚举
5. 特别检查:
   - services/buyback.py: VaultItemStatus 的值 (BUYBACK, DELIVERED) 是否在正确的枚举中存在
   - services/market.py: UserVaultStatus 的值 (VAULTED, LISTED, SOLD) 是否匹配
   - tests/test_marketplace.py, test_buyback.py, test_pack_engine.py: 枚举 import 是否正确
**约束**: 不改业务逻辑，只统一枚举定义和导入

## Task 10: Wallet API 前后端对齐
**文件**: `backend/app/api/wallet.py`, `backend/app/schemas/wallet.py`
**问题**: 前端 walletApi.ts 和后端响应结构完全不匹配
**修复**:
1. GET /wallet/balance 响应改为: `{ usdc: str, points: str, stripe_customer_id: Optional[str] }`
   - usdc = str(balance) where currency == "USDC"
   - points = str(credit_balance from user) or "0"
2. POST /wallet/deposit/stripe/intent 响应添加 `checkout_url` 字段 (如果用 Stripe Checkout Session 而非 Payment Intent)
3. POST /wallet/deposit/usdc/confirm 确认请求 schema 需要 tx_hash 字段 (已有就不改)
4. GET /wallet/history 响应改为包含 `transactions`, `total`, `page`, `page_size` 字段
5. POST /wallet/withdraw — 添加这个端点 (接收 amount + wallet_address, 创建提现请求记录)
**约束**: 只改 wallet.py 和 schemas/wallet.py

## Task 11: Pack confirm-payment 返回 revealed_items
**文件**: `backend/app/api/pack.py`
**问题**: POST /packs/openings/{openingId}/confirm-payment 只返回 `{ status, opening_id }`, 前端需要 `revealed_items` 数组
**修复**:
1. 读 schemas/pack.py 找到 PackOpenResultResp 的定义
2. 修改 api/pack.py 的 confirm-payment 端点，让它返回 PackOpenResultResp (包含 revealed_items)
3. 在 confirm 后查询 UserVault 表获取该 opening_id 对应的所有 vault items 作为 revealed_items
**约束**: 只改 api/pack.py，不改 service 层

## Task 12: Vault API 添加 NFT 元数据 + Admin CRUD
**文件**: `backend/app/api/vault.py`, `backend/app/schemas/vault.py` (如果存在), `backend/app/api/admin.py`
**问题**:
1. Vault 响应缺 nft_name, nft_image 字段
2. Admin NFT CRUD 端点是 NotImplementedError
**修复**:
1. Vault: 在返回 vault items 时 join NFT 表获取 name 和 image，添加到响应中
2. Admin: 实现 GET /admin/nfts (分页查询), POST /admin/nfts (创建), PATCH /admin/nfts/{id} (更新), DELETE /admin/nfts/{id} (软删除)
3. Admin: 实现 POST /admin/packs (创建), DELETE /admin/packs/{id} (软删除)
**约束**: 不动前端代码
