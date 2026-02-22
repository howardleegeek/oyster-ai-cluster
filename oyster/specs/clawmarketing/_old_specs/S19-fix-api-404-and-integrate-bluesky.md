---
task_id: S19-fix-api-404-and-integrate-bluesky
project: clawmarketing
priority: 1
depends_on: []
modifies: ["backend/main.py", "backend/routers/"]
executor: glm
---

## 目标
1. 修复 API 404 问题（路由前缀没注册）
2. 整合 bluesky-poster 模块到 ClawMarketing

## 问题分析
当前 API 返回 404，是因为 router 前缀没正确配置。

## 具体改动

### 1. 修复 API 路由
检查 backend/routers/ 下的每个 router，确保有正确的 @router.prefix

### 2. 整合 Bluesky Agent
复制/链接 bluesky-poster 模块到 backend/agents/bluesky/
- client.py
- queue.py
- worker.py
- rate_limiter.py
- scheduler.py
- analytics.py
- feed_discovery.py

创建统一的 Agent 接口：
```python
# backend/agents/base.py
class SocialAgent(ABC):
    @abstractmethod
    def post(self, content: str, media: list = None) -> dict: ...
    
    @abstractmethod
    def schedule(self, content: str, post_at: datetime) -> dict: ...
    
    @abstractmethod
    def get_stats(self) -> dict: ...
```

### 3. 注册 Bluesky Router
在 main.py 添加 bluesky router

## 验收标准
- [ ] /health 返回 200
- [ ] /auth/login 返回正确响应（非 404）
- [ ] /brands, /personas, /accounts 等 API 正常
- [ ] bluesky agent 可导入
