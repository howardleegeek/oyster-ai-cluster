---
task_id: F04-cm-pomelli-import
project: marketing-stack
priority: 2
estimated_minutes: 20
depends_on: []
modifies: ["clawmarketing/backend/routers/content.py"]
executor: glm
---
## 目标
Add Pomelli asset import to ClawMarketing content router - import from local pomelli/ directory or Pomelli API

## 约束
- Add POST /content/import/pomelli endpoint
- Accept local file path or Pomelli URL
- Download/copy asset to storage
- Create content item with metadata
- Support images and videos

## 验收标准
- [ ] POST /content/import/pomelli endpoint implemented
- [ ] Accepts file path or URL
- [ ] Downloads/copies asset to storage
- [ ] Creates content item with metadata
- [ ] Supports both images and videos
- [ ] pytest tests/backend/routers/test_content.py passes

## 不要做
- Don't build Pomelli integration (use simple import)
- Don't add content editing
- Don't implement AI asset generation
