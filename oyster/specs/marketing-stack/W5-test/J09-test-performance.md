---
task_id: J09-test-performance
project: marketing-stack
priority: 5
estimated_minutes: 20
depends_on: []
modifies: ["oyster/tests/e2e/test_performance_benchmarks.py"]
executor: glm
---
## 目标
Performance benchmarks: n8n workflow latency <5s, PostHog query <2s, content generation <30s, post queue processing <60s per job

## 约束
- Benchmark 1: n8n workflow execution time (10 runs avg)
- Benchmark 2: PostHog API query time (10 runs avg)
- Benchmark 3: Content generation (ALwrity/templates, 10 runs avg)
- Benchmark 4: Queue job processing time (10 runs avg)
- Record results, fail if thresholds exceeded

## 验收标准
- [ ] test_performance_benchmarks.py created
- [ ] n8n workflow avg <5s
- [ ] PostHog query avg <2s
- [ ] Content generation avg <30s
- [ ] Queue processing avg <60s per job
- [ ] pytest test_performance_benchmarks.py passes
- [ ] Benchmark report generated

## 不要做
- No load testing
- No optimization during test
- No production impact
