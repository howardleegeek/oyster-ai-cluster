---
task_id: S006-common-content-db
project: marketing-stack
priority: 1
estimated_minutes: 20
depends_on: ["S001-common-directory"]
modifies: ["oyster/social/common/content_db.py"]
executor: glm
---

## 目标
Add platform column to content database for multi-platform tracking

## 约束
- Copy oyster/social/bluesky-poster/bluesky/content_db.py → common/
- Add `platform TEXT` column to content_history and reply_history tables
- Add platform parameter to track_post() and track_reply()
- Default platform="bluesky" for backward compatibility

## 验收标准
- [ ] oyster/social/common/content_db.py exists
- [ ] Schema migration adds platform column with default "bluesky"
- [ ] track_post(platform="bluesky") and track_reply(platform="bluesky") work
- [ ] get_recent_posts() filters by platform
- [ ] pytest tests verify multi-platform isolation
- [ ] Existing data preserved with platform="bluesky"

## 不要做
- Don't change SQLite to PostgreSQL
- Don't add complex migrations - simple ALTER TABLE
- Don't refactor query logic
