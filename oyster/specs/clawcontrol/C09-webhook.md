---
task_id: C09-webhook
project: clawcontrol
priority: 1
depends_on: []
modifies:
  - pipeline/clawcontrol/api/webhook.py
---

## 目标
添加 Webhook 回调支持

## 具体改动
1. Webhook 配置
2. 任务完成回调
3. 支持 Slack/Telegram
