---
task_id: S005-common-llm-client
project: marketing-stack
priority: 1
estimated_minutes: 10
depends_on: ["S001-common-directory"]
modifies: ["oyster/social/common/llm_client.py"]
executor: glm
---

## 目标
Move LLM client to common layer (already platform-agnostic)

## 约束
- Copy oyster/social/bluesky-poster/bluesky/llm_client.py → common/
- No code changes needed - already generic
- Keep all existing LLM interaction logic

## 验收标准
- [ ] oyster/social/common/llm_client.py exists
- [ ] All LLM client functions copied without modification
- [ ] pytest tests pass
- [ ] No functionality changes

## 不要做
- Don't modify LLM client logic
- Don't add new LLM providers
- Don't refactor - just copy
