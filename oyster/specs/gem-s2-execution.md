# GEM Sprint 2 Execution Spec — 盲盒引擎收尾 + 前端对接

> 基于 S1 产出重新评估。后端 7 个 subtask 中 5 个已由 S1 实现，S2 实际工作 = 后端 bug 修复 + 前端对接 + 测试补全。

## 0. 现状评估

### 后端 (已完成 ~85%)
| S2 Subtask | 文件 | 状态 | 剩余 |
|------------|------|------|------|
| ST1 Pack/Vault 模型 | models/pack.py, schemas/pack.py, enums.py | ✅ 完成 | 无 |
| ST2 Pack/Vault Repo | db/pack.py, db/vault.py | ✅ 完成 | 无 |
| ST3 抽卡引擎 | services/pack_engine.py | ✅ 完成 | 无 |
| ST4 支付确认 | services/payment.py, db/payment.py | ✅ 完成 | 无 |
| ST5 API Router | api/pack.py, api/vault.py | ⚠️ 有 bug | 3 处修复 |
| ST6 前端 Pack Store 对接 | App.tsx, PackOpening.tsx | ❌ 硬编码 | 重写 |
| ST7 Dashboard Vault 对接 | DashboardUpdates.tsx | ✅ 完成 | 无 |

### 前端 (已完成 ~40%)
- packApi.ts / vaultApi.ts: ✅ 已存在且正确
- DashboardUpdates.tsx: ✅ 已对接 vaultApi
- App.tsx: ❌ 硬编码 PACKS 数组 + 直接调 sendSolPayment
- PackOpening.tsx: ❌ 使用 Math.random() 客户端 RNG

---

## 1. 任务拆分 (DAG)

```yaml
# 无依赖，可全部并行
P1: gem-s2-backend-bugfix    # 后端 3 处 bug 修复
P2: gem-s2-frontend-packstore # 前端 Pack Store 对接后端
P3: gem-s2-test-completion    # 测试补全

# DAG
P1 ──┐
P2 ──┤──> P4 (集成验证)
P3 ──┘
```

---

## 2. P1: 后端 Bug 修复 (GLM, 低复杂度)

### 目标
修复 S1 留下的 3 处后端 bug，不改架构不加功能。

### 修复清单

#### Bug 1: vault.py `current_user` 访问方式不一致
- **文件**: `backend/app/api/vault.py`
- **问题**: 使用 `current_user.user_id` (属性访问)，但 pack.py 使用 `current_user["user_id"]` (字典访问)
- **修复**: 统一为 `current_user["user_id"]`，与 pack.py 保持一致
- **影响行**: 约 line 32, 56 及其他引用 current_user 的位置

#### Bug 2: vault.py `nft_meta` 变量未绑定
- **文件**: `backend/app/api/vault.py`
- **问题**: 循环中引用 `nft_meta.name` / `nft_meta.image_url` 但未正确解构
- **修复**: 确保三元组 `(item, nft, nft_meta)` 正确解包
- **影响行**: 约 line 49-50, 89-90

#### Bug 3: pack.py `amount_sol` hasattr 检查
- **文件**: `backend/app/api/pack.py`
- **问题**: `hasattr(req, 'amount_sol')` 但 `PackPaymentConfirmReq` schema 无此字段
- **修复**: 移除 hasattr 检查，金额从 DB 的 opening 记录获取（已在 purchase 时保存）
- **影响行**: 约 line 256

### 约束
- **不动**: models/, schemas/, services/, db/ 层
- **不动**: 任何 UI/CSS/样式代码
- **不加**: 新功能、新 endpoint

### 验收
- `python -c "from app.api.vault import router"` 无报错
- `python -c "from app.api.pack import router"` 无报错
- 现有 pytest 全部通过

---

## 3. P2: 前端 Pack Store 对接后端 (GLM, 中复杂度)

### 目标
App.tsx 和 PackOpening.tsx 从硬编码切换到后端 API，删除客户端 RNG。

### 修改清单

#### 3.1 App.tsx 改造
- **删除**: 硬编码 `PACKS` 数组 (约 line 27-52)
- **删除**: 硬编码 `POTENTIAL_HITS` 数组 (约 line 54-61)
- **新增**: `useEffect` mount 时调用 `packApi.listPacks()` 获取 pack 列表
- **新增**: `useState` 管理 packs 数据 + loading/error 状态
- **修改**: `handleOpenPack` 流程改为:
  1. `packApi.purchasePack(packId, quantity)` → 获取 `opening_id` + `amount_sol` + `receiver_wallet`
  2. `sendSolPayment(receiver_wallet, amount_sol)` → 获取 `tx_hash`
  3. `packApi.confirmPayment(opening_id, tx_hash)` → 获取 `revealed_items`
  4. 传 `revealed_items` 给 `PackOpening` 组件

#### 3.2 PackOpening.tsx 改造
- **删除**: `Math.random()` 抽卡逻辑 (约 line 26-54)
- **新增**: `props.revealedItems` 接收后端返回的开包结果
- **保留**: 所有动画效果、UI 样式不变
- **修改**: 卡片渲染从随机生成改为读取 `revealedItems` 数组

#### 约束 (铁律)
- **不动**: GemCard.tsx, Navbar.tsx, WalletPanel.tsx 等其他组件
- **不动**: 任何 CSS/Tailwind 样式类
- **不动**: packApi.ts, vaultApi.ts (已正确实现)
- **不加**: 新依赖
- **保留**: 所有动画效果原样

### 验收
- Pack 列表来自 `/api/v1/packs` (Network tab 可见)
- 购买流程: purchase → pay → confirm 三步完成
- PackOpening 不含 `Math.random` 调用
- UI 外观与 S1 完全一致

---

## 4. P3: 测试补全 (GLM, 中复杂度)

### 目标
补全 S2 spec 中定义的 21 个 pytest case，确保覆盖所有 edge case。

### 已有测试
- `test_pack_engine.py` (527 行) — TestPackPurchase, TestPackOpening, TestPackEngineEdgeCases
- `test_vault.py` (128 行) — TestVaultRepoCreateItems, TestVaultRepoListItems, TestVaultRepoGetItem

### 需要验证/补全的测试 (来自 S2 spec)
```
ST1:
  - test_drop_table_sum_must_equal_100()
  - test_pack_status_becomes_sold_out_when_supply_reaches_max()
  - test_pack_price_decimal_roundtrip()

ST2:
  - test_reserve_supply_rejects_when_insufficient_stock()
  - test_rarity_fallback_when_target_pool_empty()
  - test_user_lock_prevents_parallel_openings()

ST3:
  - test_open_pack_is_idempotent_for_same_opening()
  - test_engine_uses_secrets_random_not_math_random()
  - test_recovery_job_opens_paid_unopened_records()

ST4:
  - test_tx_hash_duplicate_is_idempotent()
  - test_amount_mismatch_outside_tolerance_rejected()
  - test_rpc_fallback_tries_secondary_endpoint()

ST5:
  - test_purchase_pack_recomputes_price_from_db()
  - test_purchase_pack_rejects_quantity_gt_10()
  - test_confirm_payment_returns_opened_items()
```

### 执行方式
1. 先跑现有 pytest，记录哪些 pass/fail
2. 对照上面清单，找出缺失的 test case
3. 补写缺失的 test（不改业务代码）
4. 全部 pytest 通过

### 约束
- **不动**: 任何业务代码
- 测试放在 `backend/tests/` 目录
- 用 pytest + unittest.mock

---

## 5. P4: 集成验证 (Codex, P1+P2+P3 完成后)

### 验收清单
- [ ] 后端启动无报错 (`uvicorn app.app:app`)
- [ ] 全部 pytest 通过 (`pytest backend/tests/ -v`)
- [ ] 前端 build 无报错 (`cd lumina && npm run build`)
- [ ] Pack 列表从 API 加载 (不含硬编码)
- [ ] PackOpening 不含 Math.random
- [ ] 购买流程端到端: purchase → sendSOL → confirm → reveal
- [ ] 开包结果存入 vault，Dashboard 可见
- [ ] S2 spec 18 个 edge case 全部覆盖

---

## 6. Dispatch 计划

```
P1 (backend-bugfix)  → GLM (glm-node-2 或 Mac-2), ~15 min
P2 (frontend-pack)   → GLM (glm-node-2 或 Mac-2), ~30 min
P3 (test-completion) → GLM (codex-node-1 或 Mac-2), ~30 min
--- P1/P2/P3 并行 ---
P4 (integration)     → Codex (Mac-2, 需 Chrome CDP 测试), ~20 min
```

**总预计**: 50 分钟 (并行) + 验证
