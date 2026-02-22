---
task_id: S06-content-templates
project: bluesky-poster
priority: 0
estimated_minutes: 30
depends_on: []
modifies: ["bluesky/content_templates.py"]
executor: glm
---

## Goal

Create content template library with 8 post types per account.

## Context

- Reference: `/Users/howardli/Downloads/oyster/social/bluesky-automation/content_engine.py` lines 128-213 (TEMPLATES dict)
- Templates have [VARIABLE] slots that get filled dynamically
- Each template should have engagement probability rating
- Used by content_engine to generate original posts
- See `SHARED_CONTEXT.md` for project-wide conventions

## Implementation

Create `/Users/howardli/Downloads/oyster/social/bluesky-poster/bluesky/content_templates.py`:

```python
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Template:
    text: str
    variables: List[str]  # e.g. ["TOPIC", "NUMBER"]
    engagement_score: float  # 0.0-1.0 predicted engagement
    post_type: str  # vision, question, usage, etc.
```

Define 8 post types per account:
1. **vision**: Big picture statements, mission-driven
2. **question**: Open-ended questions to community
3. **day_n/usage**: Real usage stories, Day N updates
4. **comparison**: Product/tech comparisons
5. **thread**: Thread starters
6. **hot_take**: Controversial/unpopular opinions
7. **emotional**: Gratitude, celebration, community love
8. **workflow**: How-to, productivity tips

Each account gets 3-5 templates per type (total 24-40 templates per account).

Functions:
```python
TEMPLATES: Dict[str, Dict[str, List[Template]]] = {...}

def get_template(handle: str, post_type: str) -> Template:
    """Get random template for account + type"""

def fill_template(template: Template, **kwargs) -> str:
    """Fill template variables"""

def get_high_engagement_templates(handle: str, min_score: float = 0.7) -> List[Template]:
    """Get templates with high predicted engagement"""
```

**Template Format Example**:
```python
Template(
    text="Day [N] with ClawGlasses: wore them for [ACTIVITY]. [RESULT].",
    variables=["N", "ACTIVITY", "RESULT"],
    engagement_score=0.75,
    post_type="usage"
)
```

## Tests

- `test_content_templates.py`: Load templates, verify all accounts have all 8 types
- Test get_template() returns valid template
- Test fill_template() replaces all variables
- Test engagement scores are 0.0-1.0

## Acceptance Criteria

- [ ] All 3 accounts have 8 post types
- [ ] Each post type has 3-5 template variants
- [ ] Templates have [VARIABLE] slots clearly marked
- [ ] Engagement scores assigned based on historical patterns
- [ ] fill_template() handles missing variables gracefully
- [ ] Tests pass: `pytest tests/test_content_templates.py -v`

## Do NOT

- Do not add hard-coded specific content (templates should be flexible)
- Do not exceed 300 chars per template
- Do not include hashtags in templates (added separately)
