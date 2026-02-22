---
task_id: S002-common-queue
project: marketing-stack
priority: 1
estimated_minutes: 15
depends_on: ["S001-common-directory"]
modifies: ["oyster/social/common/queue.py"]
executor: glm
---

## 目标
Extract queue management from bluesky-poster to common layer with platform parameter

## 约束
- Copy from oyster/social/bluesky-poster/bluesky/queue.py
- Add `platform: str` field to Job dataclass
- Default platform="bluesky" for backward compatibility
- Keep all existing functionality working

## 验收标准
- [ ] oyster/social/common/queue.py exists
- [ ] Job dataclass has `platform: str = "bluesky"` field
- [ ] add_job(), get_next_job(), mark_completed() accept platform parameter
- [ ] pytest tests verify multi-platform queue isolation
- [ ] Existing bluesky-poster tests still pass (no regression)

## 不要做
- Don't change SQLite schema structure (just add column)
- Don't refactor existing bluesky-poster code yet
- Don't add async
