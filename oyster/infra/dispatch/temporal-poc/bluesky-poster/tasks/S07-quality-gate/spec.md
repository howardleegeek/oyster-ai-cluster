## Goal

Content quality validation with structural checks and bad reply filter.

## Context

- Reference: `/Users/howardli/Downloads/oyster/products/clawmarketing/backend/agents/quality_gate.py`
- Must reject template phrases, spam, bad replies
- Bluesky max length: 300 chars (vs Twitter 280)
- Critical for maintaining authentic engagement
- See `SHARED_CONTEXT.md` for project-wide conventions

## Implementation

Create `/Users/howardli/Downloads/oyster/social/bluesky-poster/bluesky/quality_gate.py`:

```python
from dataclasses import dataclass
from typing import List

@dataclass
class QualityResult:
    passed: bool
    score: float  # 0.0-1.0
    issues: List[str]

class QualityGate:
    def __init__(self, min_score: float = 0.7):
        self.min_score = min_score
```

**Structural Checks**:
1. Length: 5-300 chars (Bluesky limit)
2. Template phrases: Reject ["Great point", "Love this", "So true", "Exactly", "支持！", "好棒"]
3. Spam keywords: Reject ["click here", "buy now", "check out my", "link in bio"]
4. Bad replies: Reject pure emoji, single word praise, generic positivity
5. Taboo filter: Check against persona taboos list

**Quality Scoring (0.0-1.0)**:
- 1.0: Has opinion, natural language, specific to post content
- 0.7: Generic but okay
- 0.5: Template-y but passes structural
- 0.0: Fails structural checks

Functions:
```python
def check(self, text: str, persona=None) -> QualityResult:
    """Run all structural checks"""

def is_bad_reply(self, text: str) -> bool:
    """Detect low-quality replies"""

def check_taboos(self, text: str, taboos: List[str]) -> QualityResult:
    """Check against persona taboo list"""
```

**Bad Reply Patterns**:
- Pure emoji (no text)
- Single word: "Nice", "Cool", "Awesome"
- Generic praise: "Great point!", "Love this!"
- Chinese low-effort: "支持！", "好棒", "赞"
- Over-enthusiastic: Multiple exclamation marks, all caps

## Tests

- `test_quality_gate.py`: Test all checks pass/fail correctly
- Test bad reply detection
- Test taboo filter
- Test scoring ranges

## Acceptance Criteria

- [ ] Rejects all template phrases
- [ ] Rejects bad replies (pure emoji, generic praise)
- [ ] Length check: 5-300 chars
- [ ] Taboo filter works with persona-specific taboos
- [ ] Quality score is consistent (same input = same score)
- [ ] Tests pass: `pytest tests/test_quality_gate.py -v`

## Do NOT

- Do not call LLM for quality checks (keep it fast, structural only)
- Do not add dependencies beyond stdlib
- Do not make it too strict (aim for 70% pass rate on good content)