---
task_id: S016-pipeline-tests
project: article-pipeline
priority: 0
estimated_minutes: 30
depends_on: ["S014-pipeline-orchestrator"]
modifies: ["oyster/social/article-pipeline/tests/test_integration.py", "oyster/social/article-pipeline/tests/conftest.py"]
executor: glm
---

## 目标
Integration tests for the full article pipeline. Mock all external services (LLM, Twitter, TwitFast).

## 约束
- Python 3.11+, pytest, pytest-asyncio
- Test scenarios:
  1. test_full_pipeline_dry_run: trends → article → save (no publish)
  2. test_quality_gate_reject: article with low quality gets rejected
  3. test_quality_gate_revise: article gets revised and passes second time
  4. test_tweet_thread_structure: thread has hook + insights + CTA
  5. test_trend_deduplication: similar trends merged
  6. test_partial_failure: one adapter fails, pipeline continues with others
  7. test_no_trends: pipeline handles empty trend results gracefully
- Use conftest.py for shared fixtures (mock LLM, mock DB, mock Twitter)
- All tests must pass without any external API calls

## 验收标准
- [ ] 7 test scenarios all pass
- [ ] conftest.py with reusable fixtures
- [ ] No external API calls in tests
- [ ] pytest runs in < 10 seconds
- [ ] Coverage > 80% for orchestrator module

## 不要做
- No E2E tests with real APIs (just integration with mocks)
