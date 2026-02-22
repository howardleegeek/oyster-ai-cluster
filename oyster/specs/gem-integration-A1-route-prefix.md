# Task A1: 后端路由添加 /api/v1 前缀

## 目标
修改 backend/app/app.py，让所有路由都带 `/api/v1` 前缀，与前端 API 调用对齐。

## 文件
- `backend/app/app.py`

## 具体改动

找到路由注册循环（约第 71-77 行）：

```python
for router, prefix, tags in _routers:
    if prefix:
        app.include_router(router, prefix=prefix, tags=tags)
    elif tags:
        app.include_router(router, tags=tags)
    else:
        app.include_router(router)
```

修改为统一添加 `/api/v1` 前缀：

```python
API_PREFIX = "/api/v1"

for router, prefix, tags in _routers:
    full_prefix = f"{API_PREFIX}{prefix}" if prefix else API_PREFIX
    if tags:
        app.include_router(router, prefix=full_prefix, tags=tags)
    else:
        app.include_router(router, prefix=full_prefix)
```

注意：`/health` 端点如果是直接定义在 app 上的（`@app.get("/health")`），则不受影响，保留在根路径。如果 health 是通过 router 注册的，也需要加前缀变为 `/api/v1/health`。

## 验证
1. 启动后端：`cd backend && python -c "from app.app import app; print([r.path for r in app.routes])"`
2. 确认所有路由都以 `/api/v1/` 开头
3. 确认 `/health` 或 `/api/v1/health` 可访问
