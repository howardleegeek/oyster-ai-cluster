---
task_id: S04-infra-capability-scan
project: open-source-research
priority: 1
estimated_minutes: 30
depends_on: []
modifies: ["research/infra-capability-scan.md"]
executor: codex
---

## 目标
搜索 GitHub 上最佳的基础设施能力层开源项目。这些不是按产品匹配，而是按**能力模块**匹配 — 任何 Oyster 项目都可能用到。

## 搜索清单

### 分布式系统
1. **分布式任务调度** — 搜索: "distributed task scheduler python", "ray celery temporal", "job queue"
2. **工作流编排** — 搜索: "workflow orchestration", "temporal prefect airflow", "dag scheduler"
3. **BFT 共识** — 搜索: "byzantine fault tolerance", "bft consensus library", "tendermint cometbft"
4. **P2P 节点通信** — 搜索: "libp2p peer discovery", "p2p network library python"
5. **服务网格** — 搜索: "service mesh", "envoy istio", "microservice communication"

### AI/ML 基础设施
6. **RAG 框架** — 搜索: "rag framework", "haystack llamaindex langchain", "retrieval augmented generation"
7. **向量数据库** — 搜索: "vector database", "qdrant milvus chromadb weaviate"
8. **模型服务** — 搜索: "llm serving", "vllm ollama text-generation-inference"
9. **Prompt 管理** — 搜索: "prompt management", "prompt engineering framework", "promptfoo"
10. **AI 可观测性** — 搜索: "llm observability", "langsmith langfuse phoenix", "ai monitoring"

### DevOps & 安全
11. **身份认证** — 搜索: "identity management open source", "ory kratos keycloak", "auth framework"
12. **密钥管理** — 搜索: "secret management", "vault sops", "key rotation"
13. **监控告警** — 搜索: "monitoring alerting", "grafana prometheus", "uptime monitoring"
14. **日志聚合** — 搜索: "log aggregation", "loki elasticsearch", "structured logging"
15. **CI/CD 管线** — 搜索: "ci cd pipeline", "github actions dagger", "build automation"

### 数据 & 存储
16. **时序数据库** — 搜索: "time series database", "timescaledb influxdb questdb"
17. **消息队列** — 搜索: "message queue", "rabbitmq nats redis streams kafka"
18. **缓存层** — 搜索: "caching layer", "redis dragonfly garnet"

## 输出格式

按能力分类输出：

```markdown
## [能力类别]

### [能力名称]
| Repo | Stars | License | 语言 | 成熟度(1-10) | 集成难度 | 推荐 |
|------|-------|---------|------|------------|---------|------|
| owner/repo | 数字 | 许可证 | 语言 | 评分 | 低/中/高 | 是/备选 |

**最佳选择**: [repo] — [一句话理由]
**集成方式**: [如何接入现有系统]
```

## 约束
- Stars > 500
- 必须有 Python 或 TypeScript SDK
- 优先可自部署的项目
- 特别标注哪些可以替代我们现有 dispatch 系统的子模块

## 验收标准
- [ ] 18 个能力类别都有结果
- [ ] 每个至少 2 个候选
- [ ] 包含成熟度和集成难度评分
- [ ] 有明确的 "最佳选择" 推荐
