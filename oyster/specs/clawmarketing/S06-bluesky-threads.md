---
task_id: S06-bluesky-threads
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - backend/agents/thread_builder.py
---

## 目标

实现 Thread/Reply Chain 支持。

## 约束

- **不动 UI/CSS**

## 具体改动

### ThreadBuilder (`backend/agents/thread_builder.py`)

```python
class ThreadBuilder:
    """Build multi-post threads"""
    
    async def split_into_thread(self, text: str, max_length: int = 300) -> list[str]:
        """Split long content into thread posts"""
        pass
    
    async def post_thread(self, posts: list[str], account_id: int, with_images: list = None) -> list[dict]:
        """Post thread and return URIs"""
        pass
    
    async def post_reply_chain(self, parent_uri: str, replies: list[str]) -> list[dict]:
        """Post reply chain to existing post"""
        pass
    
    async def quote_tweet_with_media(self, text: str, media: list, original_uri: str) -> dict:
        """Post quote-tweet with media"""
        pass
```

### Thread 策略

- 自动拆分长内容 (300 char/post)
- 最后一条自动加 "🧵"
- 引用原文时自动带链接
- 支持多图轮播

### 示例

```
原始: "10 things about AI..."
拆分为:
[1/5] 10 things about AI you need to know 🧵
[2/5] 1. AI is accelerating faster than anyone expected...
[3/5] 2. Hardware is the bottleneck...
...
[5/5] Want more? Follow for part 2!
```

## 验收标准

- [ ] 能拆分长内容为 thread
- [ ] 能自动 post thread
- [ ] 能 post reply chain
- [ ] 支持引用+媒体

## 不要做

- ❌ 不改 UI
