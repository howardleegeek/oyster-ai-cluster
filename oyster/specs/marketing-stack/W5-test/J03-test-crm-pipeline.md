---
task_id: J03-test-crm-pipeline
project: marketing-stack
priority: 5
estimated_minutes: 20
depends_on: [E05-twenty-deploy, E08-twenty-integration, E11-twenty-workflow]
modifies: ["oyster/tests/e2e/test_crm_pipeline.py"]
executor: glm
---
## 目标
Test CRM pipeline: web visitor (PostHog event) → n8n → Twenty lead created → welcome email triggered

## 约束
- Simulate PostHog page view event
- Trigger n8n CRM workflow
- Verify lead created in Twenty
- Check welcome email sent
- Validate data consistency across systems
- Clean up test data

## 验收标准
- [ ] test_crm_pipeline.py created
- [ ] PostHog event simulated correctly
- [ ] n8n workflow triggered
- [ ] Lead appears in Twenty CRM
- [ ] Welcome email sent to test address
- [ ] pytest test_crm_pipeline.py passes
- [ ] Test data cleaned up

## 不要做
- No real visitor tracking
- No production CRM records
- No actual sales follow-up
