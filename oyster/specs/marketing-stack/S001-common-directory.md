---
task_id: S001-common-directory
project: marketing-stack
priority: 1
estimated_minutes: 15
depends_on: []
modifies: ["oyster/social/common/__init__.py", "oyster/social/common/models.py"]
executor: glm
---

## 目标
Create common protocol and models for multi-platform social media posting

## 约束
- Python 3.11+
- Use typing.Protocol for PlatformAdapter
- Use dataclasses for all models
- No external dependencies beyond stdlib

## 验收标准
- [ ] oyster/social/common/__init__.py exists with PlatformAdapter Protocol
- [ ] Protocol has methods: post(text, images) -> PostResult, reply(text, parent_id) -> PostResult, get_metrics(post_id) -> Metrics, search(query, limit) -> list[Post]
- [ ] oyster/social/common/models.py exists with PostResult, Metrics, Post dataclasses
- [ ] All type hints are complete and correct
- [ ] pytest oyster/social/common/test_models.py passes (create simple tests)

## 不要做
- Don't implement any concrete platform adapters yet
- Don't add async/await (keep sync for now)
- Don't add database code
