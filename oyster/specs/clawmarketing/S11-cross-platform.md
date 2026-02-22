---
task_id: S11-cross-platform
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - backend/services/cross_platform.py
---

## 目标

实现 Cross-Platform Syndication，一键发到多平台。

## 约束

- **不动 UI/CSS**

##具体改动

### CrossPlatform

```python
class CrossPlatform:
    """One-click post to multiple platforms"""
    
    PLATFORMS = ["bluesky", "twitter", "mastodon"]
    
    async def syndicate(self, content: str, platforms: list[str], media: list = None) -> dict:
        """Post to multiple platforms"""
        
    async def adapt_content(self, content: str, platform: str) -> str:
        """Adapt content for platform"""
        
    async def get_platform_status(self) -> dict:
        """Get connected platform status"""
```

### 功能

- Bluesky + Twitter + Mastodon
- 平台适配 (字符限制等)
- 统一发布接口

## 验收标准

- [ ] 能发到多个平台
- [ ] 能适配内容
- [ ] 有状态检查

## 不要做

- ❌ 不改 UI
