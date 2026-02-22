---
task_id: S108-mvp-workflow
project: clawmarketing
priority: 1
depends_on: ["S104-writer-agent", "S105-twitter-client", "S107-brand-api"]
modifies: ["backend/workflows/marketing_workflow.py", "backend/main.py"]
executor: glm
---
## 目标
实现 MVP Agent 工作流串联: Analyst → Writer → Twitter 发布

## 约束
- 串联已实现的 Agent 和 Client
- 不新建超过 2 个文件
- 写 pytest 测试
- 工作流有状态追踪 (pending → analyzing → writing → publishing → done/failed)

## 验收标准
- [ ] pytest tests/test_marketing_workflow.py 全绿
- [ ] POST /api/v1/campaigns/run 触发完整流程
- [ ] 工作流状态可通过 GET /api/v1/campaigns/{id}/status 查询
- [ ] 每步结果都被记录

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
