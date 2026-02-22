---
task_id: S061-ab-testing
project: marketing-stack
priority: 3
estimated_minutes: 30
depends_on: [A01-unified-db, B04-posthog-deploy]
modifies: ["oyster/social/common/ab_testing.py"]
executor: glm
---
## 目标
Create A/B testing engine: create test variants, track results, determine winner with statistical significance

## 约束
- Methods: create_test(variants), track_result(variant, metric), determine_winner(min_sample=100, confidence=0.95)
- Integrate PostHog feature flags for web tests
- Store in unified.db: ab_tests, ab_results tables
- Statistical test: chi-square or t-test
- Export report as JSON/markdown

## 验收标准
- [ ] ab_testing.py created with class ABTest
- [ ] Can create multi-variant tests
- [ ] track_result() records metrics correctly
- [ ] determine_winner() uses statistical significance
- [ ] PostHog integration for web experiments
- [ ] pytest tests pass with sample data
- [ ] CLI: python -m ab_testing create/track/report

## 不要做
- No auto-optimization yet
- No multi-armed bandit
- No UI dashboard
