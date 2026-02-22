---
task_id: S008-common-templates
project: marketing-stack
priority: 1
estimated_minutes: 15
depends_on: ["S001-common-directory"]
modifies: ["oyster/social/common/content_templates.py"]
executor: glm
---

## 目标
Move content templates to common with platform field

## 约束
- Copy oyster/social/bluesky-poster/bluesky/content_templates.py → common/
- Add `platform: str = "bluesky"` field to Template dataclass
- Keep all existing templates

## 验收标准
- [ ] oyster/social/common/content_templates.py exists
- [ ] Template dataclass has `platform: str = "bluesky"` field
- [ ] All existing templates work with default platform
- [ ] get_template(), list_templates() accept optional platform filter
- [ ] pytest tests verify platform-specific template filtering
- [ ] No existing functionality broken

## 不要做
- Don't modify template content
- Don't add new templates yet
- Don't change template structure beyond platform field
