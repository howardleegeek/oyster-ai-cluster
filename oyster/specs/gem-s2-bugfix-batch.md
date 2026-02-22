# GEM S2 Byzantine Bug Fix Spec — 3 Batch Parallel

> 拜占庭 20 分队验证发现 5 CRITICAL + 13 HIGH bugs。分 3 个 batch 并行修复。

---

## Batch 1: CRITICAL — 开包引擎 (最高优先)

**节点**: glm-node-2 或 codex-node-1
**文件范围**: `services/pack_engine.py`, `services/payment.py`, `api/nft.py`

### Fix C1: draw_rarity() float vs Decimal TypeError
- **文件**: `app/services/pack_engine.py` 约 line 60
- **问题**: `self._rng.uniform(0, 100)` 返回 float，但 `cumulative` 是 Decimal，比较 `roll <= cumulative` 抛 TypeError
- **修复**: 将 roll 转为 Decimal: `roll = Decimal(str(self._rng.uniform(0, 100)))`
- **同时修复 H9**: line 72 fallback 返回 `sorted_drops[-1]`（最低概率=LEGENDARY），应返回 `sorted_drops[0]`（最高概率=COMMON）

### Fix C3: NFT 选择并发安全
- **文件**: `app/services/pack_engine.py` 约 line 104-111
- **问题**: `_draw_nft_for_rarity_direct` 选 NFT 时无 `FOR UPDATE`，并发开包拿到同一 NFT
- **修复**:
  1. 查询加 `.with_for_update(skip_locked=True)` 跳过已锁行
  2. 选到 NFT 后立即更新 status 为 CLAIMED（或类似标记）
  3. 如果查询返回空（全被锁），触发 rarity fallback

### Fix C2: NftPayment nft_id=None
- **文件**: `app/api/pack.py` 约 line 297
- **问题**: 创建 `NftPayment(nft_id=None)` 但 model 定义 `nullable=False`
- **修复**:
  - 方案 A: 将 `nft.py` 中 NftPayment.nft_id 改为 `nullable=True`（pack 支付时还没有 nft_id，开包后才关联）
  - 方案 B: 不在 confirm-payment 步骤创建 NftPayment，改为在 open_pack 后用实际 nft_id 创建
  - **推荐方案 A**（改动最小）

### Fix C4: PaymentService Session 未 import
- **文件**: `app/services/payment.py` line 1-10
- **问题**: 使用 `Session` 类型注解但未 import
- **修复**: 添加 `from sqlalchemy.orm import Session`

### Fix C5: nft.py ext_service import
- **文件**: `app/api/nft.py` line 12
- **问题**: `from app.ext_service import *` 模块不存在
- **修复**: 删除该 import 行。如果导致 NameError 需要查看哪些名字来自 ext_service 并直接 import

### 约束
- 不动 UI/CSS
- 不动 schemas 层（除非 C2 方案 B）
- 每个 fix 改完后跑 `python -c "from app.services.pack_engine import PackEngineService; print('OK')"`

---

## Batch 2: HIGH — API 层 + 事务安全

**节点**: Mac-2
**文件范围**: `api/pack.py`, `services/pack_engine.py`, `services/pack.py`

### Fix H1: SOLD_OUT pack 拒绝开包
- **文件**: `app/services/pack_engine.py` 约 line 187-188
- **问题**: `open_pack` 检查 `pack.status != ACTIVE` 就拒绝，但最后一个买家购买后 pack 变 SOLD_OUT
- **修复**: 允许 SOLD_OUT 状态的 pack 继续开包，只拒绝 CANCELLED/EXPIRED:
  ```python
  if pack.status in (PackStatus.CANCELLED, PackStatus.EXPIRED):
      raise PackNotAvailableError(...)
  ```

### Fix H2: confirm_payment_and_open 三次 commit
- **文件**: `app/api/pack.py` 约 line 221-326
- **问题**: 3 次独立 commit，crash 后状态不一致
- **修复**:
  1. 移除 `pack_engine.py` 内部的 `self.db.commit()`（line 216）
  2. 让 `confirm_payment_and_open` 统一在最后一次 commit
  3. 用 try/except 包裹，失败时 rollback

### Fix H3: NFT 分配后状态不更新
- **文件**: `app/services/pack_engine.py` 约 line 204-211
- **问题**: drawn NFT 没标记为已分配，仍在可用池
- **修复**: 开包后 `nft.status = 'CLAIMED'` 或等效状态更新

### Fix H4: tx_hash 竞态
- **文件**: `app/api/pack.py` 约 line 287-293
- **问题**: tx_hash 唯一性检查是普通 SELECT，两个并发请求可能都通过
- **修复**: 用 try/except 捕获 `IntegrityError`，如果 UNIQUE 违反则返回已有记录（幂等）

### Fix H13: PackPaymentConfirmReq 重复定义
- **文件**: `api/pack.py:35` + `schemas/pack.py:26`
- **问题**: 同一个 schema 定义了两次
- **修复**: 删除 `api/pack.py` 中的定义，使用 `from app.schemas.pack import PackPaymentConfirmReq`

### 约束
- 不动 models 层（Batch 3 做）
- 不动 UI
- 事务改动必须用 try/except/rollback

---

## Batch 3: HIGH — Models 层修复

**节点**: glm-node-2 或 codex-node-1
**文件范围**: `models/*.py`

### Fix H5 + H6: Shadow Enums
- **文件**: `models/wallet.py`, `models/order.py`
- **问题**: 本地重新定义 DepositStatus/DepositType/RedemptionOrderStatus 与 enums.py 不一致
- **修复**:
  1. 删除本地 enum 定义
  2. 改为 `from app.models.enums import DepositStatus, DepositType, RedemptionOrderStatus`
  3. 如果 enums.py 缺少某些值（如 CUSTOMS_HOLD），在 enums.py 中补充

### Fix H7: price_sol 精度
- **文件**: `models/pack.py` line 26
- **修复**: `DECIMAL(20,8)` → `DECIMAL(20,9)`

### Fix H8: fmv 精度
- **文件**: `models/pack.py` line 122
- **修复**: `DECIMAL(20,2)` → `DECIMAL(20,6)`

### Fix H10: Frontend GemMetadata import
- **文件**: `lumina/App.tsx` line 10
- **修复**: 添加 `GemMetadata` 到 import: `import { Pack, Gem, ViewState, Rarity, GemStatus, GemMetadata } from './types'`

### Fix H11: mock_tx_hash fallback
- **文件**: `lumina/components/ActionModals.tsx` line 241
- **修复**:
  ```typescript
  // Before: txHash || 'mock_tx_hash'
  // After:
  if (!txHash) throw new Error('Transaction hash is required');
  ```

### Fix H12: Missing ForeignKeys (低优先，不影响运行)
- **暂缓**: 15+ 个 user_id 列缺 FK，需要数据库迁移。标记为 Sprint 3 TODO。

### 约束
- 不动 service/api 层
- Decimal 精度改动需要 alembic migration（或手动 ALTER TABLE）
- 前端改动后跑 `npm run build`

---

## Dispatch 计划

```
Batch 1 (CRITICAL) → GLM glm-node-2    ~30 min
Batch 2 (HIGH API) → GLM Mac-2          ~30 min
Batch 3 (HIGH Models + FE) → GLM codex-node-1  ~20 min
--- 全部并行 ---
```

## 验收标准
1. `python -c "from app.app import app; print(len(app.routes))"` → 无报错
2. `pytest tests/ -v` → 全部 pass
3. `cd lumina && npm run build` → 无报错
4. `grep -r "Math.random" lumina/components/PackOpening.tsx` → 0 结果
5. `grep -r "mock_tx_hash" lumina/` → 0 结果
