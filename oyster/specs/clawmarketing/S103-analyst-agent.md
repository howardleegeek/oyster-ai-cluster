---
task_id: S103-analyst-agent
project: clawmarketing
priority: 1
depends_on: ["S100-llm-router-base"]
modifies: ["backend/agents/analyst_agent.py", "backend/models/schemas.py"]
executor: glm
---
## 目标
实现 Analyst Agent — 分析品牌需求，输出内容 brief

## 约束
- 使用 LLM Router 调用模型
- 不新建超过 2 个文件
- 写 pytest 测试
- Analyst 输入: brand_name, goal, context
- Analyst 输出: AnalysisBrief(target_audience, key_messages, tone, content_suggestions)

## 验收标准
- [ ] pytest tests/test_analyst_agent.py 全绿
- [ ] Analyst Agent 接收品牌分析需求返回结构化 brief
- [ ] brief 包含 target_audience, key_messages, tone 字段
- [ ] 使用 Pydantic schema 验证输入输出

## 不要做
- 不动 frontend
- 不改 main.py 的路由结构
- 不留 TODO/FIXME/placeholder — 所有逻辑必须实现
