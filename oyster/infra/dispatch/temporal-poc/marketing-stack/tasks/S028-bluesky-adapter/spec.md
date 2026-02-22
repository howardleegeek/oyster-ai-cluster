## 目标
Create oyster/social/bluesky/adapter.py wrapping existing bluesky-poster/bluesky/client.py as thin PlatformAdapter implementation

## 约束
- Thin wrapper around bluesky-poster/bluesky/client.py
- Must implement PlatformAdapter Protocol from A01
- Reuse existing authentication and posting logic
- No major refactoring of existing code

## 验收标准
- [ ] adapter.py implements PlatformAdapter Protocol
- [ ] post() wraps existing client.post()
- [ ] reply() wraps existing reply functionality
- [ ] get_metrics() returns basic engagement data
- [ ] search() returns posts from feeds
- [ ] pytest tests/social/bluesky/test_adapter.py passes

## 不要做
- Don't rewrite bluesky-poster client logic
- Don't add heavy dependencies
- Don't change existing bluesky-poster API

## FALLBACK PROTOCOL INITIATED
Previous attempts continuously failed. Final error:
```
Activity cancelled
```

**CRITICAL INSTRUCTION**: Abandon your previous approach. Simplify your solution, use alternative methods, or stub the functionality safely. Do NOT repeat the same mistakes.