---
task_id: S121-test-listening-pipeline
project: marketing-stack
priority: 5
estimated_minutes: 15
depends_on: [E12-obsei-workflow]
modifies: ["oyster/tests/e2e/test_listening_pipeline.py"]
executor: glm
---
## 目标
Test social listening pipeline: brand mention detected by Obsei → n8n alert → response draft generated

## 约束
- Simulate brand mention (test tweet/post)
- Obsei detects mention via API
- n8n receives alert
- Response draft generated (ALwrity or template)
- Validate sentiment scoring

## 验收标准
- [ ] test_listening_pipeline.py created
- [ ] Test mention created and detected
- [ ] Obsei sentiment score calculated
- [ ] n8n alert triggered
- [ ] Response draft generated
- [ ] pytest test_listening_pipeline.py passes

## 不要做
- No real brand monitoring
- No auto-response to real mentions
- No production social accounts
