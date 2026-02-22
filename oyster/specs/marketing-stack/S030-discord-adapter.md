---
task_id: S030-discord-adapter
project: marketing-stack
priority: 2
estimated_minutes: 25
depends_on: [A01]
modifies: ["oyster/social/discord/adapter.py"]
executor: glm
---
## 目标
Create oyster/social/discord/adapter.py implementing PlatformAdapter Protocol wrapping discord.py bot library

## 约束
- Wrap discord.py bot library
- post() sends message to specified channel
- search() retrieves channel history
- Must handle bot authentication via token
- Store bot token in ~/.oyster-keys/
- Support channel ID specification

## 验收标准
- [ ] adapter.py implements PlatformAdapter Protocol
- [ ] post() sends messages to Discord channels
- [ ] search() retrieves message history
- [ ] Bot authentication works with stored token
- [ ] Channel targeting by ID works correctly
- [ ] pytest tests/social/discord/test_adapter.py passes

## 不要做
- Don't build full Discord bot features (slash commands, etc.)
- Don't add UI for channel management
- Don't store tokens in code
