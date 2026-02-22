---
task_id: J02-test-email-pipeline
project: marketing-stack
priority: 5
estimated_minutes: 20
depends_on: [E03-listmonk-workflow, E11-twenty-workflow]
modifies: ["oyster/tests/e2e/test_email_pipeline.py"]
executor: glm
---
## 目标
Test email pipeline: content generated → Listmonk campaign → subscriber receives → open/click tracked in PostHog

## 约束
- Create test subscriber list
- Generate test email content
- Send via Listmonk
- Verify delivery to test email
- Track open/click events in PostHog
- Clean up test data after

## 验收标准
- [ ] test_email_pipeline.py created
- [ ] Test subscriber created in Listmonk
- [ ] Email campaign sent successfully
- [ ] Test email received and verified
- [ ] PostHog shows open/click events
- [ ] pytest test_email_pipeline.py passes
- [ ] Test data cleaned up

## 不要做
- No real subscriber lists
- No production email sending
- No spam testing
