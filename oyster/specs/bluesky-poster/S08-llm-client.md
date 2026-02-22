---
task_id: S08-llm-client
project: bluesky-poster
priority: 0
estimated_minutes: 40
depends_on: []
modifies: ["bluesky/llm_client.py"]
executor: glm
---

## Goal

Simple httpx-based Anthropic API client for content generation.

## Context

- Reference: `/Users/howardli/Downloads/oyster/social/twitter-poster/engagement_farmer.py` lines 400-450 (claude_generate_reply)
- No complex dependencies, just httpx + Anthropic API
- Must construct system prompt: humanize preamble + persona system_prompt + context
- Fallback to templates if LLM fails
- See `SHARED_CONTEXT.md` for project-wide conventions

## Implementation

Create `/Users/howardli/Downloads/oyster/social/bluesky-poster/bluesky/llm_client.py`:

```python
import httpx
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-20250514"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

# Humanize preamble (prepended to all system prompts)
HUMANIZE_PREAMBLE = """
CRITICAL RULES FOR SOUNDING HUMAN:
1. BREVITY: Real people write 5-20 words, not essays.
2. IMPERFECTION: Drop commas, use 'gonna', start lowercase. Perfect = AI.
3. NO SYCOPHANCY: Never compliment. No "great point", "love this", "so true".
4. NO CORPORATE: Never "leverage", "ecosystem", "paradigm", "innovative".
5. HAVE AN OPINION: Agree or disagree. Wishy-washy = AI.
6. ONE THOUGHT: React to ONE thing, not everything.
7. NATURAL FLOW: Sound like a text to a friend, not LinkedIn.
8. NO HASHTAGS in replies.
9. NO EMOJI SPAM: Zero or one emoji max.
"""
```

Functions:
```python
async def generate_reply(
    persona,
    post_text: str,
    post_author: str,
    context: Optional[dict] = None
) -> str:
    """Generate reply to a post"""

async def generate_post(
    persona,
    post_type: str,
    topic: Optional[str] = None,
    context: Optional[dict] = None
) -> str:
    """Generate original post"""

def _build_system_prompt(persona, context: Optional[dict] = None) -> str:
    """Build complete system prompt"""
```

**System Prompt Construction**:
```
{HUMANIZE_PREAMBLE}

{persona.system_prompt}

CURRENT CONTEXT:
- Your handle: {persona.handle}
- Your topics: {persona.topics}
- Taboos: {persona.taboos}
- Style: {persona.style}

{additional context if provided}
```

**Error Handling**:
- Timeout: 30s
- Retry: 1 retry on 5xx errors
- Fallback: Return None if all retries fail (caller handles fallback to templates)

## Tests

- `test_llm_client.py`: Mock Anthropic API, test reply generation
- Test system prompt construction
- Test error handling and fallback
- Test timeout

## Acceptance Criteria

- [ ] Successfully calls Anthropic API with httpx
- [ ] System prompt includes humanize preamble + persona prompt
- [ ] generate_reply() returns 5-50 word replies
- [ ] generate_post() returns 50-280 char posts
- [ ] Handles API errors gracefully (returns None)
- [ ] Tests pass: `pytest tests/test_llm_client.py -v`

## Do NOT

- Do not add complex LLM routing (single provider, Anthropic only)
- Do not hardcode API key in code (use env var ANTHROPIC_API_KEY)
- Do not retry more than once (fail fast)
