---
task_id: S01-infra-backend-setup
project: clawphones-backend
priority: 1
depends_on: []
modifies:
  - ~/Downloads/clawphones-backend/app/auth/
  - ~/Downloads/clawphones-backend/app/chat/
  - ~/Downloads/clawphones-backend/app/admin/
  - ~/Downloads/clawphones-backend/app/files/
executor: glm
---

## 目标
创建 ClawPhones 后端基础设施和核心 API 模块

## 具体改动

### 1. 创建 app/auth/ 模块 (新增)
创建以下文件:
- `app/auth/__init__.py` - 模块初始化
- `app/auth/auth_router.py` - 路由定义，包含:
  - POST /v1/auth/register
  - POST /v1/auth/login
  - POST /v1/auth/refresh
  - GET /v1/user/profile
  - PUT /v1/user/profile
- `app/auth/auth_service.py` - 业务逻辑
- `app/auth/auth_models.py` - SQLAlchemy 模型

### 2. 创建 app/chat/ 模块 (新增)
创建以下文件:
- `app/chat/__init__.py`
- `app/chat/chat_router.py` - 路由，包含:
  - POST /v1/chat/completions
  - POST /v1/conversations
  - GET /v1/conversations
  - POST /v1/conversations/{id}/chat/stream
- `app/chat/chat_service.py` - 使用 plugins.ai
- `app/chat/chat_models.py`

### 3. 创建 app/admin/ 模块 (新增)
创建以下文件:
- `app/admin/__init__.py`
- `app/admin/admin_router.py` - 路由，包含:
  - POST /admin/tokens/generate
  - POST /admin/tokens/{token}/tier
  - POST /admin/tokens/{token}/disable
- `app/admin/admin_service.py`

### 4. 创建 app/files/ 模块 (新增)
创建以下文件:
- `app/files/__init__.py`
- `app/files/files_router.py` - 路由:
  - POST /v1/upload
  - GET /v1/files/{file_id}
- `app/files/files_service.py`

### 5. 配置 plugins/ai.py
编辑 `app/plugins/ai.py`，确保:
- provider 可配置 (deepseek/kimi/claude)
- tier 路由逻辑: free→DeepSeek, pro→Kimi, max→Claude
- 环境变量: DEEPSEEK_API_KEY, KIMI_API_KEY, ANTHROPIC_API_KEY

### 6. 注册路由到 main.py
在 `app/main.py` 中添加:
```python
from app.auth import auth_router
from app.chat import chat_router
from app.admin import admin_router
from app.files import files_router

app.include_router(auth_router, prefix="/v1")
app.include_router(chat_router, prefix="/v1")
app.include_router(admin_router, prefix="/admin")
app.include_router(files_router, prefix="/v1")
```

## 验收标准
- [ ] app/auth/ 目录和文件存在
- [ ] app/chat/ 目录和文件存在
- [ ] app/admin/ 目录和文件存在
- [ ] app/files/ 目录和文件存在
- [ ] main.py 包含所有路由
- [ ] pytest tests/test_health.py 可运行

## 不要做
- 不修改现有 iOS/Android 代码
