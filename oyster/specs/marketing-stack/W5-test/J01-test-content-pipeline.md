---
task_id: J01-test-content-pipeline
project: marketing-stack
priority: 5
estimated_minutes: 20
depends_on: [E09-postiz-workflow]
modifies: ["oyster/tests/e2e/test_content_pipeline.py"]
executor: glm
---
## 目标
Test full content pipeline: Pomelli asset → n8n → Postiz → post published → analytics tracked, verify end-to-end

## 约束
- Create test Pomelli output (sample image/video)
- Trigger n8n workflow manually
- Verify Postiz receives content
- Check post publishes to test account
- Confirm PostHog/Plausible track the post
- All steps logged and verifiable

## 验收标准
- [ ] test_content_pipeline.py created
- [ ] Test runs full pipeline end-to-end
- [ ] Each stage verified (Pomelli → n8n → Postiz → publish → analytics)
- [ ] Test passes with green status
- [ ] Logs show each step completion
- [ ] pytest test_content_pipeline.py passes

## 不要做
- No production account posting
- No real audience targeting
- No paid promotion testing
