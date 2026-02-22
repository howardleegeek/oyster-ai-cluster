---
task_id: S06-discord-community-integration
project: clawphones-backend
priority: 2
depends_on: []
modifies:
  - ~/Downloads/clawphones-backend/app/plugins/discord.py
  - ~/Downloads/clawphones-backend/app/community/
executor: glm
---

## 目标
集成 Discord 社区运营，使用 INFRA plugins.discord

## 约束
- 使用 backend 内置的 plugins.discord
- 不修改现有移动端代码

## 具体改动

### 1. 配置 plugins.discord
编辑 ~/Downloads/clawphones-backend/app/plugins/discord.py:
```python
settings = {
    "enabled": True,
    "bot_token": os.getenv("DISCORD_BOT_TOKEN"),
    "guild_id": os.getenv("DISCORD_GUILD_ID"),
    "channel_announcements": os.getenv("DISCORD_CHANNEL_ANNOUNCEMENTS"),
    "channel_support": os.getenv("DISCORD_CHANNEL_SUPPORT"),
}
```

### 2. 创建 Community 模块
创建 app/community/:
- app/community/__init__.py
- app/community/community_router.py:
  - GET /v1/communities - 社区列表
  - POST /v1/communities - 创建社区
  - GET /v1/communities/{id} - 社区详情
  - POST /v1/communities/{id}/join - 加入社区
  - POST /v1/communities/{id}/leave - 离开社区
- app/community/community_service.py:
  - sync_discord() - Discord 同步
  - post_announcement() - 公告推送

### 3. Discord 集成功能
```python
# 同步用户到 Discord
async def sync_user_to_discord(user):
    # 创建 Discord 角色
    # 分配频道权限
    pass

# 社区事件通知到 Discord
async def notify_discord_community(community_id, event):
    channel = get_community_channel(community_id)
    await discord.send_message(channel, event)
```

### 4. 配置环境变量
```
DISCORD_BOT_TOKEN=xxx
DISCORD_GUILD_ID=xxx
DISCORD_CHANNEL_ANNOUNCEMENTS=xxx
DISCORD_CHANNEL_SUPPORT=xxx
```

## 验收标准
- [ ] Discord 插件配置正确
- [ ] /v1/communities 端点可用
- [ ] Discord 同步功能正常
- [ ] 测试通过

## 不要做
- 不改 iOS/Android 客户端代码
