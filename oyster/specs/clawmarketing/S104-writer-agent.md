---
task_id: S104-writer-agent
project: clawmarketing
priority: 1
depends_on: ["S103-analyst-agent"]
modifies: ["backend/agents/writer_agent.py", "backend/models/schemas.py"]
executor: glm
---
## 目标
实现 Writer Agent — 基于 Analyst brief 生成推文内容

## 约束
- 使用 LLM Router 调用模型
- 复用 Analyst Agent 输出的 AnalysisBrief
- 写 pytest 测试
- Writer 输出: TweetDraft(content, hashtags, media_suggestions, platform)
- 推文长度限制 280 字符

## 验收标准
- [ ] pytest tests/test_writer_agent.py 全绿
- [ ] Writer Agent 接收 AnalysisBrief 返回 TweetDraft
- [ ] 生成的推文不超过 280 字符
- [ ] 包含至少 1 个 hashtag

## 不要做
- 不动 frontend
- 不改 main.py 的路由结构
- 不留 TODO/FIXME/placeholder
