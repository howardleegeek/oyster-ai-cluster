---
task_id: S070-obsei-deploy
project: marketing-stack
priority: 3
estimated_minutes: 25
depends_on: []
modifies: ["oyster/infra/obsei-config/", "oyster/social/common/obsei_listener.py"]
executor: glm
---
## 目标
Deploy Obsei social listening for Twitter/Reddit brand mentions + competitor keywords, sentiment analysis, alerts on negative sentiment

## 约束
- Sources: Twitter (6 brand keywords + competitor terms), Reddit (relevant subreddits)
- Sentiment: default model (VADER or transformers)
- Alert rule: sentiment score < 0.3
- Store results in SQLite: mentions table
- Cron: every 15 minutes
- Output format: JSON + alert webhooks

## 验收标准
- [ ] Obsei installed and configured
- [ ] Twitter/Reddit sources active
- [ ] Sentiment scores calculated correctly
- [ ] SQLite mentions table populated
- [ ] Alerts fire for negative sentiment
- [ ] Python script obsei_listener.py runs via cron

## 不要做
- No auto-response yet
- No Instagram/Facebook (API limits)
- No complex NLP analysis
