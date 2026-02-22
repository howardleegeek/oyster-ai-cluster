---
task_id: D01-twitter-adapter
project: marketing-stack
priority: 2
estimated_minutes: 30
depends_on: [A01]
modifies: ["oyster/social/twitter/adapter.py"]
executor: glm
---
## 目标
Create oyster/social/twitter/adapter.py implementing PlatformAdapter Protocol with post(), reply(), get_metrics(), search() methods

## 约束
- Extract core posting logic from twitter-poster/twitter_poster.py
- Use existing RapidAPI/CDP modes
- Must implement PlatformAdapter Protocol from A01
- Handle rate limiting gracefully
- Return structured responses matching protocol

## 验收标准
- [ ] adapter.py implements all PlatformAdapter methods
- [ ] post() successfully posts to Twitter using existing RapidAPI/CDP
- [ ] reply() successfully replies to tweets
- [ ] get_metrics() returns engagement data
- [ ] search() returns relevant tweets
- [ ] pytest tests/social/twitter/test_adapter.py passes

## 不要做
- Don't rewrite existing RapidAPI/CDP integration
- Don't add new dependencies beyond protocol interface
- Don't modify twitter-poster/twitter_poster.py
