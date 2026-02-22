---
task_id: J07-test-fallback
project: marketing-stack
priority: 5
estimated_minutes: 30
depends_on: []
modifies: ["oyster/tests/e2e/test_fallback_resilience.py"]
executor: glm
---
## 目标
Test all fallback paths: kill n8n → verify cron fallback, kill PostHog → verify Plausible tracks, LLM unavailable → verify template fallback

## 约束
- Test 1: Stop n8n, verify cron jobs continue
- Test 2: Block PostHog API, verify Plausible still tracks
- Test 3: Simulate LLM API failure, verify templates used
- Restore all services after tests
- Document fallback behavior

## 验收标准
- [ ] test_fallback_resilience.py created
- [ ] n8n fallback test passes (cron works)
- [ ] PostHog fallback test passes (Plausible works)
- [ ] LLM fallback test passes (templates used)
- [ ] All services restored to normal
- [ ] pytest test_fallback_resilience.py passes
- [ ] Fallback behavior documented

## 不要做
- No permanent service shutdown
- No data loss
- No production impact
