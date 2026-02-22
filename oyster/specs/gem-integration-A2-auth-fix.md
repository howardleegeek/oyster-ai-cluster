# Task A2: 后端 auth 依赖修复

## 目标
将所有使用 placeholder auth 的端点改为使用真正的 JWT 验证依赖。

## 背景
- 真正的 `get_current_user` 实现在 `backend/app/services/auth.py` 第 565-576 行
- 已有 `CurrentUserDep = Annotated[UserPrincipal, Depends(get_current_user)]`
- 有些文件用 `Depends(lambda: None)` 占位
- 有些文件（wallet.py）自己定义了 placeholder 版本

## Bug Fix (必须先修)
`backend/app/services/auth.py` 的 `parse_token` 方法（约第 490-494 行）缺少 `role` 字段：

找到:
```python
return UserPrincipal(
    user_id=user_id,
    email=email or user.email,
    wallet_version=wallet_version
)
```

改为:
```python
return UserPrincipal(
    user_id=user_id,
    email=email or user.email,
    wallet_version=wallet_version,
    role=role
)
```

确认 `role` 变量已在上面的代码中从 payload 提取（约第 477 行附近应该有 `role = payload.get("role", "user")`）。如果没有，添加提取逻辑。

## 文件修改清单

### 1. `backend/app/api/wallet.py`
- **删除** 第 22-39 行的本地 `get_current_user` placeholder 函数和 `HTTPBearer` 定义
- **添加** import: `from app.services.auth import get_current_user, CurrentUserDep`
- **替换** 所有端点中的 auth 参数为 `current_user: CurrentUserDep`

### 2. `backend/app/api/order.py`
- **修改** import: 不要从 wallet.py 导入 `get_current_user`
- **改为**: `from app.services.auth import get_current_user, CurrentUserDep`
- **替换** 所有端点中的 auth 参数

### 3. `backend/app/api/referral.py`
- **修改** import: 不要从 wallet.py 导入 `get_current_user`
- **改为**: `from app.services.auth import get_current_user, CurrentUserDep`
- **替换** 所有端点中的 auth 参数

### 4. `backend/app/api/market.py`
- **替换** 所有 `Depends(lambda: None)` 为 `current_user: CurrentUserDep`
- **添加** import: `from app.services.auth import CurrentUserDep`
- 涉及约 6 个端点：list, delist, buy, create offer, respond offer, my offers

### 5. `backend/app/api/buyback.py`
- **替换** 所有 `Depends(lambda: None)` 为 `current_user: CurrentUserDep`
- **添加** import: `from app.services.auth import CurrentUserDep`
- 涉及约 3 个端点：request buyback, cancel, list requests

### 6. `backend/app/api/admin.py`
- **替换** `get_current_admin` placeholder
- **添加** import: `from app.services.auth import get_current_user, CurrentUserDep`
- 创建真正的 admin 验证：
```python
async def get_current_admin(
    current_user: CurrentUserDep,
) -> UserPrincipal:
    if current_user.role not in ("admin", "super_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

AdminUserDep = Annotated[UserPrincipal, Depends(get_current_admin)]
```
- 所有 admin 端点使用 `admin: AdminUserDep`

## 验证
1. Python 语法检查: `cd backend && python -c "from app.api import market, buyback, wallet, admin, order, referral; print('OK')"`
2. 不带 token 请求 market/buyback/wallet 端点应返回 401/403
