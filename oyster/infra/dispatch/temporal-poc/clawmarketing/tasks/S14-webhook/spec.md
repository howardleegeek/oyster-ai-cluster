## 目标

实现 Webhook System，外部事件触发发帖。

## 约束

- **不动 UI/CSS**

##具体改动

### WebhookSystem

```python
class WebhookSystem:
    """Trigger posts from external events"""
    
    async def register_webhook(self, url: str, event: str, action: str):
        """Register webhook"""
        
    async def trigger(self, event: str, payload: dict):
        """Trigger action from event"""
        
    async def handle_rss(self, feed_url: str, filter: str = None):
        """Handle RSS feed"""
        
    async def handle_news_alert(self, source: str):
        """Handle news alerts"""
```

### 支持的事件

- RSS feed 更新
- 新闻警报
- 产品发布
- 自定义 webhook

## 验收标准

- [ ] 能注册 webhook
- [ ] 能触发动作
- [ ] 支持 RSS

## 不要做

- ❌ 不改 UI