---
task_id: S11-customer-docs
project: dispatch-productize
priority: 2
estimated_minutes: 45
depends_on: ["S10-docker-production"]
modifies: ["oyster/infra/dispatch/README.md", "oyster/infra/dispatch/docs/"]
executor: glm
---

## 目标

创建面向客户的文档，让客户能够自助部署和使用 dispatch 系统。

## 实现

### README.md
```markdown
# Oyster Dispatch — AI Agent Orchestration System

Distributed task orchestration for AI coding agents.

## Quick Start
docker-compose up -d

## Features
- Distribute coding tasks to AI agent workers
- DAG dependency resolution
- Automatic retry with exponential backoff
- Worker health monitoring and auto-recovery
- PostgreSQL persistence (production) / SQLite (development)
- Docker Compose one-click deployment

## Architecture
[简洁架构图]

## Configuration
[环境变量表]

## API Reference
[Controller API endpoints]

## CLI Reference
[dispatch.py commands]
```

### docs/ 目录
1. `docs/quickstart.md` — 5 分钟快速开始
2. `docs/architecture.md` — 系统架构说明
3. `docs/configuration.md` — 完整配置参考
4. `docs/api-reference.md` — Controller HTTP API
5. `docs/cli-reference.md` — dispatch.py CLI 命令
6. `docs/deployment.md` — 生产部署指南
7. `docs/worker-setup.md` — Worker 节点配置
8. `docs/troubleshooting.md` — 常见问题排查

## 约束

- 英文文档（面向国际客户）
- 每个文档不超过 200 行
- 代码示例可直接复制运行
- 不暴露内部实现细节

## 验收标准

- [ ] README.md 包含 Quick Start 可直接运行
- [ ] 8 个文档文件全部创建
- [ ] 代码示例语法正确
- [ ] 无拼写错误

## 不要做

- 不写中文文档（后续 spec）
- 不暴露内部 API
- 不写 SDK 文档（后续 spec）
