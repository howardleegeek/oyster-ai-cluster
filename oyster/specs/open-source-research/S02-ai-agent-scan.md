---
task_id: S02-ai-agent-scan
project: open-source-research
priority: 1
estimated_minutes: 30
depends_on: []
modifies: ["research/ai-agent-scan.md"]
executor: codex
---

## 目标
搜索 GitHub 上最佳的 AI/Agent 开源项目，为 Oyster Labs 以下项目找到可直接 Fork 使用的替代方案。

## 搜索清单

1. **AI 编码 Agent** — 搜索: "ai coding agent", "autonomous software engineer", "swe-agent", "openhands opendevin"
2. **AI 销售自动化** — 搜索: "ai sales automation", "open source crm ai", "sales intelligence agent"
3. **AI 合同审查** — 搜索: "ai contract review", "legal document analysis llm", "contract intelligence"
4. **AI 爬虫** — 搜索: "ai web crawler", "llm web scraper", "crawl4ai firecrawl"
5. **语音 AI 客服** — 搜索: "voice ai agent", "voice customer service bot", "livekit pipecat"
6. **自进化 Agent** — 搜索: "self improving ai agent", "self evolving agent", "evoagentx"
7. **边缘 LLM 推理** — 搜索: "on device llm inference", "edge llm", "llama.cpp mlc-llm"
8. **LLM 成本优化** — 搜索: "llm cost optimization", "prompt compression", "token reduction"
9. **多 Agent 框架** — 搜索: "multi agent framework", "crewai autogen langgraph"
10. **AI 内容生成** — 搜索: "ai content generation platform", "dify flowise langflow"
11. **竞情分析** — 搜索: "competitive intelligence tool", "competitor analysis ai"
12. **AR 眼镜 AI** — 搜索: "ar glasses sdk", "smart glasses os", "augmentos"
13. **AI 社交网络** — 搜索: "ai social network", "ai powered social media platform"
14. **AI 神经营销** — 搜索: "neuromarketing ai", "eye tracking analytics", "attention prediction"
15. **Deep Research** — 搜索: "gpt researcher", "deep research agent", "autonomous research"

## 输出格式

对每个项目，输出：

```markdown
### [项目名称]

| Repo | Stars | 最后更新 | License | 语言 | 匹配度 | 推荐用法 |
|------|-------|---------|---------|------|--------|---------|
| owner/repo | 数字 | YYYY-MM | 许可证 | 语言 | 高/中/低 | Fork/集成/参考 |
```

附：为什么推荐 + 如何集成到 Oyster 项目。

## 约束
- Stars > 100，最近 12 个月活跃
- 优先 Apache-2.0 / MIT
- 每个类别至少 3 个候选
- 特别注意是否有 Python SDK 或 REST API 可直接调用

## 验收标准
- [ ] 15 个类别都有结果
- [ ] 每个至少 3 个候选
- [ ] 包含完整元数据
- [ ] 有集成建议
