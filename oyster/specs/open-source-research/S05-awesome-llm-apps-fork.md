---
task_id: S05-awesome-llm-apps-fork
project: open-source-research
priority: 1
estimated_minutes: 20
depends_on: []
modifies: ["research/awesome-llm-apps-analysis.md"]
executor: codex
---

## 目标
深度分析 https://github.com/Shubhamsaboo/awesome-llm-apps 仓库，找出可直接集成到 Oyster Labs 项目的组件。

## 任务
1. Clone 或浏览 awesome-llm-apps 仓库
2. 列出所有子目录和应用
3. 对每个应用分析：
   - 技术栈 (框架、API、依赖)
   - 代码量和复杂度
   - 是否可独立运行
   - 需要哪些 API Key

4. 重点评估这些类别对 Oyster 的价值：
   - **AI Sales Agent** → 对应 ai-sales-startup
   - **AI Competitor Intelligence** → 对应 competitor-gap-driven
   - **Multi-Agent Teams** → 对应 agentforge
   - **RAG 系统** → 对应 research pipeline
   - **Voice AI** → 对应 voice-ai-for-customer-service
   - **AI Coding Agent Team** → 对应 ai-software-engineering-agent
   - **MCP Agents** → 对应 openclaw-mission-control

5. 输出推荐清单：哪些可以直接 fork 到 Oyster 项目里用

## 输出格式

```markdown
## 可直接复用的组件

| 组件 | 路径 | 技术栈 | 对应 Oyster 项目 | 复用方式 | 改造量 |
|------|------|--------|-----------------|---------|-------|
| ... | awesome-llm-apps/xxx | ... | ... | Fork/集成 | 小/中/大 |
```

## 验收标准
- [ ] 完整列出仓库所有应用
- [ ] 评估了所有 7 个重点类别
- [ ] 输出了可复用组件清单
- [ ] 每个推荐有改造量估算
