---
task_id: S05-persona-config
project: bluesky-poster
priority: 0
estimated_minutes: 25
depends_on: []
modifies: ["bluesky/personas.py"]
executor: glm
---

## Goal

Create persona configuration module with complete definitions for all 3 Bluesky accounts.

## Context

- Reference: `/Users/howardli/Downloads/oyster/social/twitter-poster/engagement_farmer.py` lines 45-150 (PERSONAS dict)
- Reference: `/Users/howardli/Downloads/oyster/social/bluesky-automation/content_engine.py` lines 75-122 (ACCOUNTS dict)
- Must support multi-account with distinct personalities
- Will be imported by reply_engine, content_engine, and llm_client
- See `SHARED_CONTEXT.md` for project-wide conventions

## Implementation

Create `/Users/howardli/Downloads/oyster/social/bluesky-poster/bluesky/personas.py`:

```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Persona:
    handle: str
    name: str
    bio: str
    topics: List[str]
    style: str  # Brief style description
    system_prompt: str  # Full LLM system prompt
    search_keywords: List[str]  # For discovery
    emotional_range: str  # "warm", "terse", "curious"
    taboos: List[str]  # What to NEVER mention
    humanize_rules: Dict[str, any]  # Lowercase %, emoji %, etc.
    content_mix: Dict[str, float]  # Ratios for post types
```

Define 3 personas:
1. **oysterecosystem**: Community voice, warm, "we" pronouns, DePIN/sovereignty focus
2. **clawglasses**: Technical, terse, YC vibe, AI hardware focus
3. **puffyai**: Curious, friendly, tool comparisons, AI agent focus

Each persona must include:
- `system_prompt`: Full prompt for LLM with personality, constraints, examples
- `taboos`: ["our product", "buy now", "check out", ...] - 95% zero product mention rule
- `humanize_rules`: `{"lowercase_start": 0.3, "drop_comma": 0.2, "emoji_rate": 0.1}`
- `content_mix`: `{"emotional": 0.25, "question": 0.25, "knowledge": 0.20, "visual": 0.15, "meme": 0.15}`

Functions:
```python
PERSONAS: Dict[str, Persona] = {...}

def get_persona(handle: str) -> Persona:
    """Get persona by handle"""

def list_personas() -> List[str]:
    """List all available persona handles"""
```

## Tests

- `test_persona_config.py`: Verify all 3 personas load, all required fields present
- Test get_persona() returns correct persona
- Test system_prompt is non-empty and contains personality markers

## Acceptance Criteria

- [ ] All 3 personas defined with complete fields
- [ ] System prompts are 150-300 words, include personality + constraints + examples
- [ ] Taboos list has 10+ items including product mentions
- [ ] Content mix ratios sum to 1.0
- [ ] Importable: `from bluesky.personas import PERSONAS, get_persona`
- [ ] Tests pass: `pytest tests/test_persona_config.py -v`

## Do NOT

- Do not add new dependencies
- Do not modify existing queue/worker/client code
- Do not hardcode API keys
