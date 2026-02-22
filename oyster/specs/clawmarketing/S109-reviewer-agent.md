---
task_id: S109-reviewer-agent
project: clawmarketing
priority: 2
depends_on: ["S108-mvp-workflow"]
modifies: ["backend/agents/reviewer_agent.py", "backend/models/schemas.py"]
executor: glm
---
## 目标
实现 Reviewer Agent — 审核推文质量和品牌调性

## 约束
- 使用 LLM Router
- 审核维度: 品牌调性一致性、语法、敏感词、长度
- 写 pytest 测试

## 验收标准
- [ ] pytest tests/test_reviewer_agent.py 全绿
- [ ] Reviewer 返回 ReviewResult(approved, score, suggestions)
- [ ] score 0-100, approved 阈值 >= 70

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
