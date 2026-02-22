---
task_id: S01-bluesky-client
project: bluesky-poster
priority: 1
depends_on: []
modifies: ["bluesky/client.py"]
executor: glm
---

## 目标
封装 atproto SDK，提供 BlueskyClient 类实现 Bluesky 所有社交操作

## 约束
- 使用 `atproto` 官方 Python SDK (`from atproto import AsyncClient`)
- 所有方法 async def，强制 kwargs
- 认证: handle + app_password (App Password，不是登录密码)
- 使用 `atproto_client.utils.TextBuilder` 构建 rich text (mentions/links/hashtags)
- 图片上传用 `client.upload_blob()`
- **必须实现错误重试机制**（网络超时、429 限流）

## 接口定义
```python
from dataclasses import dataclass

@dataclass
class PostResult:
    """发帖/回复结果"""
    uri: str           # at://did:plc:xxx/app.bsky.feed.post/xxx
    cid: str           # 内容哈希
    url: str           # https://bsky.app/profile/handle/post/xxx
    author_did: str    # 作者 DID
    timestamp: str     # ISO 时间


class BlueskyClient:
    """Bluesky AT Protocol 客户端封装"""

    def __init__(self, *, handle: str, app_password: str) -> None:
        """初始化客户端
        
        Args:
            handle: 账号 handle (如 'user.bsky.social')
            app_password: App Password (在 bsky.app 设置 → 开发 → App Password)
        """

    async def login(self) -> bool:
        """登录，返回是否成功。失败时 log 错误原因"""

    async def post(
        self, 
        *, 
        text: str, 
        images: list[tuple[bytes, str, str]] | None = None
    ) -> PostResult:
        """发帖
        
        Args:
            text: 帖子文本 (最多 300 字符)
            images: [(image_bytes, alt_text, mime_type), ...]
                - mime_type: 'image/jpeg', 'image/png', 'image/gif'
        
        Returns:
            PostResult: uri, cid, url, author_did, timestamp
        """

    async def reply(
        self, 
        *, 
        text: str, 
        parent_uri: str, 
        parent_cid: str
    ) -> PostResult:
        """回复帖子
        
        Args:
            text: 回复文本
            parent_uri: 父帖子 URI
            parent_cid: 父帖子 CID
        """

    async def like(self, *, uri: str, cid: str) -> bool:
        """点赞帖子
        
        Args:
            uri: 帖子 URI
            cid: 帖子 CID
        Returns:
            True if successful
        """

    async def repost(self, *, uri: str, cid: str) -> bool:
        """转推帖子
        
        Args:
            uri: 帖子 URI
            cid: 帖子 CID
        Returns:
            True if successful
        """

    async def follow(self, *, did: str) -> bool:
        """关注用户
        
        Args:
            did: 用户 DID
        Returns:
            True if successful
        """

    async def get_timeline(self, *, limit: int = 50) -> list[dict]:
        """获取关注者时间线
        
        Returns:
            [{uri, cid, author: {did, handle, display_name}, text, like_count, indexed_at}, ...]
        """

    async def search_posts(self, *, query: str, limit: int = 50) -> list[dict]:
        """搜索帖子
        
        Args:
            query: 搜索关键词
            limit: 返回数量 (最多 100)
        
        Returns:
            同 get_timeline 格式
        """

    async def get_post_thread(self, *, uri: str) -> dict:
        """获取帖子线程（上下文）"""

    async def get_profile(self, *, actor: str) -> dict:
        """获取用户资料
        
        Args:
            actor: handle 或 DID
        """
```

## 错误处理要求

```python
async def _request_with_retry(self, coro, *, max_retries: int = 3) -> Any:
    """带重试的请求
    
    - 网络超时: 指数退避 (2s, 4s, 8s)
    - 429 限流: 解析 Retry-After 或等待 60s
    - 5xx 错误: 等待 10s 重试
    """
```

## 验收标准
- [ ] `pytest tests/test_client.py` 全绿 (mock atproto)
- [ ] login() 成功后 self._logged_in = True
- [ ] post() 返回 PostResult 包含所有字段
- [ ] reply() 正确设置 root/parent reference
- [ ] images 上传后正确 embed 到帖子
- [ ] get_timeline() 返回标准化字段
- [ ] search_posts() 按关键词搜索返回结果
- [ ] 网络错误自动重试 3 次
- [ ] 429 限流正确处理

## 不要做
- 不创建数据库代码 (S02 负责)
- 不实现限流 (S04 负责)
- 不实现 CLI (S05 负责)
- 不实现内容生成 (S06 负责)

## SHARED_CONTEXT
见 specs/SHARED_CONTEXT.md
