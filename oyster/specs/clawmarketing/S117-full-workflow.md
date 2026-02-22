---
task_id: S117-full-workflow
project: clawmarketing
priority: 2
depends_on: ["S110-publisher-agent", "S114-agent-memory-integration", "S116-analytics-api"]
modifies: ["backend/workflows/full_workflow.py", "backend/main.py"]
executor: glm
---
## 目标
实现 Phase 2 完整 4-Agent 工作流: Analyst → Writer → Reviewer → Publisher

## 约束
- 串联所有 Agent + 记忆 + Discord 通知
- 写 pytest 测试
- 工作流支持重试和回溯

## 验收标准
- [ ] pytest tests/test_full_workflow.py 全绿
- [ ] POST /api/v1/campaigns/run-full 触发完整 4-agent 流程
- [ ] 失败步骤自动重试 (max 2 次)
- [ ] 每步结果写入 analytics

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
