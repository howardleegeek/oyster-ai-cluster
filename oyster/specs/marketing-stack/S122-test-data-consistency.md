---
task_id: S122-test-data-consistency
project: marketing-stack
priority: 5
estimated_minutes: 20
depends_on: []
modifies: ["oyster/tests/e2e/test_data_consistency.py"]
executor: glm
---
## 目标
Verify data consistency: same post shows same metrics across PostHog, Plausible, ClawMarketing dashboard, cross-reference 10 sample posts

## 约束
- Select 10 recent posts from unified queue
- Query metrics from PostHog API
- Query metrics from Plausible API
- Query ClawMarketing dashboard API
- Compare: views, clicks, engagement
- Tolerance: ±5% variance acceptable

## 验收标准
- [ ] test_data_consistency.py created
- [ ] 10 sample posts selected
- [ ] Metrics fetched from all 3 sources
- [ ] Comparison shows <5% variance
- [ ] Discrepancies logged for investigation
- [ ] pytest test_data_consistency.py passes

## 不要做
- No data modification
- No forced sync
- No ignoring major discrepancies
