# GEM S1 Fix Batch 1 — CRITICAL Code Crash Fixes

> 拜占庭验收发现 12 个 CRITICAL 崩溃问题，拆成 6 个独立任务并行修复

## Task 1: Fix MarketListing & MarketOffer Missing Fields
**文件**: `backend/app/models/market.py`
**问题**: MarketListing 缺 `transaction_hash`, `updated_at`; MarketOffer 缺 `expires_at`, `responded_at`, `transaction_hash`, `updated_at`
**修复**:
- MarketListing 添加: `transaction_hash = Column(String(128), nullable=True)`, `updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())`
- MarketOffer 添加: `expires_at = Column(DateTime, nullable=True)`, `responded_at = Column(DateTime, nullable=True)`, `transaction_hash = Column(String(128), nullable=True)`, `updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())`
- 同步更新 `backend/app/schemas/market.py` 的 MarketOfferResp 添加对应字段
**约束**: 不动任何 UI/CSS/样式代码，只改 models 和 schemas

## Task 2: Fix Pack price_sol & OpeningStatus Enum
**文件**: `backend/app/models/pack.py`, `backend/app/services/pack.py`, `backend/app/models/enums.py`
**问题**:
1. service 引用 `pack.price_sol` 但 model 只有 `price` → 在 Pack model 添加 `price_sol = Column(Numeric(20, 8), nullable=True)`
2. service import `OpeningStatus` 但 enums.py 定义的是 `PackOpeningStatus` → 改 service 的 import 为 `PackOpeningStatus`，并全局替换 `OpeningStatus.` → `PackOpeningStatus.`
3. service 引用 `Rarity` 但未 import → 添加 `from app.models.enums import Rarity`
**约束**: 只改上述 3 个文件

## Task 3: Fix Missing Imports (Session, UnauthorizedError)
**文件**: `backend/app/services/pack.py`, `backend/app/api/market.py`
**问题**:
1. `services/pack.py` 使用 `Session` 类型但未 import → 添加 `from sqlalchemy.orm import Session`
2. `api/market.py` 引用 `UnauthorizedError` 但未 import → 从 `app.error` 或正确位置 import `UnauthorizedError`
3. 检查 `VaultItemStatus` import (services/market.py line 11) → 如果 enums.py 中叫 `UserVaultStatus`，改 import
**约束**: 只改 import 语句，不改逻辑

## Task 4: Standardize CurrentUserDep Usage
**文件**: `backend/app/api/wallet.py`, `backend/app/api/market.py`, 以及所有 `backend/app/api/*.py`
**问题**: CurrentUserDep 返回 dict，但部分 API 文件用 `current_user.user_id`（错），应统一为 `current_user["user_id"]`
**修复步骤**:
1. 先读 `backend/app/api/auth.py` 确认 CurrentUserDep 返回什么 (dict 还是 object)
2. 然后统一所有 API 文件中的 current_user 访问方式
3. 用 grep 搜索 `current_user\.` 找到所有点号访问，改为 `current_user["..."]`（如果 CurrentUserDep 返回 dict）
4. 或者反过来：如果 CurrentUserDep 返回 User object，把所有 `current_user["..."]` 改为 `current_user.`
**约束**: 先确认正确方式，然后全局统一。不改 auth.py 本身的 CurrentUserDep 定义

## Task 5: Fix MarketRepo & CreateOfferRepoReq Schemas
**文件**: `backend/app/schemas/market.py`, `backend/app/db/market.py`
**问题**:
1. `CreateOfferRepoReq` 缺 `expires_at` 字段 → 添加 `expires_at: Optional[datetime] = None`
2. `MarketListingResp` 包含 `nft_id`, `rarity`, `fmv` 但 service 未填充 → 检查 market service 的 listing 查询是否 join NFT 表获取这些字段，如果没有则修复查询或从 metadata_snapshot_json 中提取
3. 检查 `MarketRepoDep` 在 `db/__init__.py` 中是否正确导出
**约束**: 只改 schemas 和 db 层

## Task 6: Fix notification router & rate limit config
**文件**: `backend/app/app.py`, `backend/app/config.py`
**问题**:
1. `app.py` 未注册 notification router → 添加 notification API 的 include_router
2. `config.py` 缺少 rate limit 配置字段 → 添加 `rate_limit_enabled: bool = True`, `rate_limit_requests_per_minute: int = 60`, `rate_limit_requests_per_hour: int = 1000`
3. 检查 `security.py` 的 RateLimiter 是否引用这些字段
**约束**: 只改 app.py 和 config.py
