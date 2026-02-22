---
task_id: S004-common-quality-gate
project: marketing-stack
priority: 1
estimated_minutes: 10
depends_on: ["S001-common-directory"]
modifies: ["oyster/social/common/quality_gate.py"]
executor: glm
---

## 目标
Move quality gate validation to common layer (already platform-agnostic)

## 约束
- Copy oyster/social/bluesky-poster/bluesky/quality_gate.py → common/
- No code changes needed - already generic
- Keep all existing validation rules

## 验收标准
- [ ] oyster/social/common/quality_gate.py exists
- [ ] All functions copied: validate_content(), check_spam_indicators(), etc.
- [ ] pytest tests pass with copied code
- [ ] No functionality changes

## 不要做
- Don't modify validation logic
- Don't add new quality checks
- Don't refactor - just copy
