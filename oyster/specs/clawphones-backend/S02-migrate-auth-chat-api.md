---
task_id: S02-migrate-auth-chat-api
project: clawphones-backend
priority: 1
depends_on: ["S01-infra-backend-setup"]
modifies:
  - ~/Downloads/clawphones-backend/app/plugins/ai.py
  - ~/Downloads/clawphones-backend/app/auth/
  - ~/Downloads/clawphones-backend/app/chat/
executor: glm
---

## 目标
迁移 Auth + Chat API，使用 INFRA 插件系统 (plugins.ai)

## 约束
- 保持 API 兼容现有客户端
- 使用 backend 内置的 plugins.ai 做 LLM 路由
- 不改变现有接口签名

## 具体改动

### 1. 配置 plugins.ai
编辑 ~/Downloads/clawphones-backend/app/plugins/ai.py:
```python
settings = {
    "enabled": True,
    "provider": "deepseek",  # 默认
    "default_model": "deepseek-chat",
}
```

添加 provider 路由逻辑:
- free → DeepSeek (deepseek-chat)
- pro → Kimi (moonshot-v1-32k) 
- max → Claude (claude-3-5-sonnet-latest)

### 2. 配置环境变量
创建 ~/Downloads/clawphones-backend/.env:
```
# AI Providers
DEEPSEEK_API_KEY=xxx
KIMI_API_KEY=xxx
ANTHROPIC_API_KEY=xxx

# Database
DATABASE_URL=postgresql://...

# Redis
REDIS_URL=redis://...
```

### 3. 创建 Auth 模块
创建 app/auth/:
- app/auth/__init__.py
- app/auth/auth_router.py:
  - POST /v1/auth/register
  - POST /v1/auth/login
  - POST /v1/auth/apple
  - POST /v1/auth/refresh
  - GET /v1/user/profile
  - PUT /v1/user/profile
  - GET /v1/user/plan
  - GET /v1/user/ai-config
  - PUT /v1/user/ai-config
- app/auth/auth_service.py
- app/auth/auth_models.py (SQLAlchemy)

### 4. 创建 Chat 模块
创建 app/chat/:
- app/chat/__init__.py
- app/chat/chat_router.py:
  - POST /v1/chat/completions
  - POST /v1/conversations
  - GET /v1/conversations
  - GET /v1/conversations/{id}
  - POST /v1/conversations/{id}/chat
  - POST /v1/conversations/{id}/chat/stream (SSE)
  - DELETE /v1/conversations/{id}
- app/chat/chat_service.py - 使用 plugins.ai.chat()
- app/chat/chat_models.py

### 5. 注册路由到 main.py
```python
from app.auth import auth_router
from app.chat import chat_router

app.include_router(auth_router, prefix="/v1")
app.include_router(chat_router, prefix="/v1")
```

## 验收标准
- [ ] plugins.ai 配置正确
- [ ] Auth API 测试通过
- [ ] Chat API 调用 LLM 正常 (DeepSeek/Kimi/Claude)
- [ ] SSE streaming 正常工作
- [ ] Token tier 路由正确

## 不要做
- 不改 iOS/Android 客户端代码
