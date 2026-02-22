## 任务: 修复 GEM Platform 后端所有 import 和依赖错误

### 背景
GEM RWA Platform 后端 (FastAPI + SQLAlchemy) 由多个 GLM 节点并行生成 Sprint 1-5 代码。
由于各节点独立生成，存在大量 import 缺失、命名不一致、Depends 模式不统一的问题。
目前只有 4/12 个 router 能成功加载 (auth, user, pack, vault)。

### 工作目录
`/Users/howardli/Downloads/gem-platform/backend/`

### 具体要求

1. **扫描所有 Python 文件**，找出并修复以下类别的错误:

   a. **缺失 import**: 引用了未导入的类/函数。常见模式:
      - `CacheDbDep` → 需要 `from app.db.cache import CacheDbDep`
      - `RankRepoDep` → 需要 `from app.db.rank import RankRepoDep`
      - 各种 `*Repo` 和 `*RepoDep` 和 `*ServiceDep`
      - `SettingsDep` → `from app.config import SettingsDep`
      - `get_settings` → `from app.config import get_settings`
      - `AdminAuthService` → 确保有正确 import

   b. **SQLAlchemy `metadata` 保留字**: 任何 model 中用 `metadata` 作为字段名的，改为 `item_metadata`，用 `mapped_column("metadata", ...)` 映射回数据库列名

   c. **FastAPI 参数顺序**: 带默认值的参数 (Query, = None) 不能在无默认值参数 (Depends) 之前。需要重排

   d. **services/__init__.py** 必须导出所有 ServiceDep:
      - NftServiceDep, AuthServiceDep, OrderServiceDep, ReferralServiceDep
      - RankServiceDep, WalletPaymentServiceDep, StripeWebhookServiceDep
      - MarketServiceDep, BuybackServiceDep
      - AdminNftServiceDep, AdminOpsServiceDep, AdminPackServiceDep

   e. **db/__init__.py** 必须导出所有 RepoDep + get_db + Base + engine + Error:
      - NftRepoDep, UserRepoDep, AuthCacheRepoDep, PackRepoDep, VaultRepoDep
      - WalletRepoDep, LedgerRepoDep, MarketRepoDep, BuybackRepoDep
      - OrderRepoDep, PaymentRepoDep, RankRepoDep, ReferralRepoDep
      - AdminNftRepoDep, AdminOpsRepoDep, AdminPackRepoDep
      - RecordAlreadyExistsError, RecordNotFoundError

   f. **models/__init__.py** 必须导出所有 model 模块 (from .xxx import *)

   g. **schemas/__init__.py** 必须导出所有 schema 模块 (from .xxx import *)

   h. **enums.py** 必须定义所有被引用的 enum: BuybackRequestStatus, VaultItemStatus, UserVaultStatus, PackStatus, OpeningStatus, Rarity, UserRole, DepositStatus, DepositType, RedemptionOrderStatus, RedemptionItemStatus, PackOpeningStatus

   i. **webhooks.py**: 第39行有 `await` outside async function — 检查函数是否需要 `async def`

   j. **market.py 和 buyback.py services**: 需要有 `MarketServiceDep` 和 `BuybackServiceDep` (Annotated Depends 模式)

2. **不要改动业务逻辑**，只修 import、类型引用、参数顺序

3. **验证**: 修完后运行:
   ```python
   python -c "from app.app import app; print('routes:', len(app.routes))"
   ```
   目标: 0 个 WARNING，所有 12 个 router 成功加载

### 已有文件结构
```
app/
├── app.py          # 主入口，try/except 加载各 router
├── config.py       # Settings + SettingsDep
├── error.py        # UserError, ServerError
├── utils.py        # SuccessResp, SettingsDep
├── api/            # 13 个 router 文件
├── db/             # 17 个 repo 文件 + base.py + err.py + cache.py
├── models/         # 14 个 model 文件 + enums.py
├── schemas/        # 14 个 schema 文件
├── services/       # 18 个 service 文件
└── plib/           # 旧的辅助库 (session_store, web3, etc.)
```

### 验收标准
- [ ] `python -c "import ast; ..."` 所有 .py 文件语法通过
- [ ] `python -c "from app.app import app"` 无 WARNING
- [ ] 所有 12 个 router 加载成功 (预期 ~60+ routes)
- [ ] 无循环 import
- [ ] 无自引用 import (file X importing from itself)
