---
task_id: S007-common-personas
project: marketing-stack
priority: 1
estimated_minutes: 10
depends_on: ["S001-common-directory"]
modifies: ["oyster/social/common/personas.py"]
executor: glm
---

## 目标
Move personas to common layer for reuse across platforms

## 约束
- Copy oyster/social/bluesky-poster/bluesky/personas.py → common/
- No structural changes - just move
- Keep all existing personas intact

## 验收标准
- [ ] oyster/social/common/personas.py exists
- [ ] All personas copied: PERSONAS dict with all entries
- [ ] get_persona(), list_personas() functions work
- [ ] pytest tests pass
- [ ] No functionality changes

## 不要做
- Don't modify existing personas
- Don't add new personas yet
- Don't refactor persona structure
