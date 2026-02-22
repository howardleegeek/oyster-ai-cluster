---
task_id: S111-discord-client
project: clawmarketing
priority: 2
depends_on: []
modifies: ["backend/clients/discord_client.py"]
executor: glm
---
## 目标
实现 Discord Webhook 客户端

## 约束
- 基于 httpx 实现
- 支持 Webhook 发送消息和 Embed
- 写 pytest 测试

## 验收标准
- [ ] pytest tests/test_discord_client.py 全绿
- [ ] DiscordClient.send_message(webhook_url, content) 正常工作
- [ ] DiscordClient.send_embed(webhook_url, embed) 支持富文本

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
