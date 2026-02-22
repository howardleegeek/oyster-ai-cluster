---
task_id: S038-cm-obsei-pull
project: marketing-stack
priority: 2
estimated_minutes: 20
depends_on: []
modifies: ["clawmarketing/backend/routers/scout.py"]
executor: glm
---
## 目标
Add Obsei data pull to ClawMarketing scout router - fetch sentiment data via Obsei API

## 约束
- Add GET /scout/sentiment endpoint
- Use Obsei API (or local Obsei instance)
- Fetch mentions with sentiment scores
- Filter by source (Twitter, Reddit, etc.)
- Return mentions with sentiment analysis

## 验收标准
- [ ] GET /scout/sentiment endpoint implemented
- [ ] Fetches mentions from Obsei
- [ ] Returns sentiment scores and source
- [ ] Supports filtering by source platform
- [ ] Error handling for API failures
- [ ] pytest tests/backend/routers/test_scout.py passes

## 不要做
- Don't build sentiment analysis from scratch
- Don't add auto-response features
- Don't implement brand monitoring alerts (E12 handles)
