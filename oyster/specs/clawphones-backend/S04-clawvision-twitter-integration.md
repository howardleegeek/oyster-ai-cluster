---
task_id: S04-clawvision-twitter-integration
project: clawphones-backend
priority: 2
depends_on: []
modifies:
  - ~/Downloads/clawphones-backend/app/plugins/twitter.py
  - ~/Downloads/clawphones-backend/app/vision/
executor: glm
---

## 目标
集成 ClawVision 事件 → Twitter 自动推送，使用 INFRA plugins.twitter

## 约束
- 使用 backend 内置的 plugins.twitter
- 不修改现有移动端代码

## 具体改动

### 1. 配置 plugins.twitter
编辑 ~/Downloads/clawphones-backend/app/plugins/twitter.py:
```python
settings = {
    "enabled": True,
    "api_key": os.getenv("TWITTER_API_KEY"),
    "api_secret": os.getenv("TWITTER_API_SECRET"),
    "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
    "access_secret": os.getenv("TWITTER_ACCESS_SECRET"),
}
```

### 2. 创建 Vision 模块
创建 app/vision/:
- app/vision/__init__.py
- app/vision/vision_router.py:
  - POST /v1/vision/events - 接收 ClawVision 事件
  - GET /v1/vision/events - 获取事件列表
  - POST /v1/vision/webhook - Webhook 接收
- app/vision/vision_service.py:
  - process_vision_event() - 处理视觉事件
  - auto_post_twitter() - 自动发推

### 3. 事件类型映射到推文
```python
def event_to_tweet(event_type: str, data: dict) -> str:
    if event_type == "motion_detected":
        return f"🚨 Motion detected at {data['location']}! #ClawVision"
    elif event_type == "package_delivered":
        return f"📦 Package delivered at {data['location']} #ClawVision"
    elif event_type == "stranger_detected":
        return f"⚠️ Stranger detected at {data['location']} #ClawVision"
    # ...
```

### 4. 配置环境变量
```
TWITTER_API_KEY=xxx
TWITTER_API_SECRET=xxx
TWITTER_ACCESS_TOKEN=xxx
TWITTER_ACCESS_SECRET=xxx
```

## 验收标准
- [ ] Twitter 插件配置正确
- [ ] /v1/vision/events 端点可用
- [ ] 事件自动发推功能正常 (可 mock 测试)
- [ ] 测试通过

## 不要做
- 不改 iOS/Android 客户端代码
