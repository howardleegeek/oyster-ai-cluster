---
task_id: S114-agent-memory-integration
project: clawmarketing
priority: 2
depends_on: ["S113-memory-service", "S104-writer-agent"]
modifies: ["backend/agents/analyst_agent.py", "backend/agents/writer_agent.py"]
executor: glm
---
## 目标
Analyst 和 Writer Agent 集成记忆系统

## 约束
- Analyst 读取历史记忆作为上下文
- Writer 保存生成结果到记忆
- 写 pytest 测试

## 验收标准
- [ ] pytest tests/test_agent_memory_integration.py 全绿
- [ ] Analyst.analyze() 自动加载品牌历史记忆
- [ ] Writer.write() 完成后自动保存到 hot memory

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
