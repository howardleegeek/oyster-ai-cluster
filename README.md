# Oyster Labs AI Cluster

> 分布式 AI 任务调度系统 — 7 节点 140 slots，团队共享

## 集群现状

```
团队成员 ──SSH──→ glm-node-2 (网关) ──→ 7 云节点 / 140 slots
                  dispatch.py 自动调度     DAG 依赖 + 文件锁 + 自动重试

┌──────────────────────────────────────────────────────────┐
│                    Cloud Nodes (共享)                     │
│                                                          │
│  GCP:                          OCI:                      │
│  ┌────────────┐ ┌────────────┐ ┌──────────────┐          │
│  │codex-node-1│ │glm-node-2  │ │oci-paid-1    │          │
│  │  8 slots   │ │  8 slots   │ │  40 slots    │          │
│  └────────────┘ └────────────┘ └──────────────┘          │
│  ┌────────────┐ ┌────────────┐ ┌──────────────┐          │
│  │glm-node-3  │ │glm-node-4  │ │oci-paid-3    │          │
│  │  8 slots   │ │  8 slots   │ │  48 slots    │          │
│  └────────────┘ └────────────┘ └──────────────┘          │
│                                ┌──────────────┐          │
│                                │oci-arm-1     │          │
│                                │  20 slots    │          │
│                                └──────────────┘          │
└──────────────────────────────────────────────────────────┘
```

## 团队成员快速开始

**详细入门指南: [docs/TEAM_QUICKSTART.md](./docs/TEAM_QUICKSTART.md)**

```bash
# 1. 把私钥放到 ~/.ssh/ 并设权限
mv ~/Downloads/<your-key> ~/.ssh/<your-key>
chmod 600 ~/.ssh/<your-key>

# 2. 登录网关
ssh -i ~/.ssh/<your-key> <your-user>@34.145.79.154

# 3. 写 spec → 跑任务
mkdir -p ~/specs/my-project
vi ~/specs/my-project/S01-my-task.md
dispatch start my-project
dispatch status my-project
```

## 核心命令

| 命令 | 用途 |
|------|------|
| `dispatch start <project>` | 启动调度（扫描 specs → 分发到节点） |
| `dispatch status [project]` | 查看任务状态和节点负载 |
| `dispatch report <project>` | 生成完成报告 |
| `dispatch collect <project>` | 收集远程结果到本地 |
| `dispatch stop <project>` | 停止调度 |
| `dispatch cleanup <project>` | 清理远程任务目录 |

## 核心文件

| 文件 | 用途 |
|------|------|
| `dispatch/dispatch.py` | 主调度器 (2400+ 行, DAG 调度 + SSH 分发) |
| `dispatch/task-wrapper.sh` | 任务执行包装器 (rate limit fallback + timeout) |
| `dispatch/agent-daemon.py` | 节点常驻 daemon (pull 模式) |
| `dispatch/slot_agent.py` | 槽位管理 Agent |
| `dispatch/session_agent.py` | 会话管理 Agent |
| `dispatch/bootstrap.sh` | 节点一键初始化脚本 |
| `dispatch/nodes.json` | 集群节点配置 |
| `dispatch/projects.json` | 项目配置 (sync 模式、路径) |

## Pipeline (CI/CD 管线)

6 层自动化管线，从分析到部署：

```
L1 Analyze → L2 Implement → L3 Build → L4 Test → L5 Fix → L6 Deploy
                                         ├── L4a API QA
                                         ├── L4b Browser QA
                                         ├── L4c UI Review
                                         └── L4d Regression
```

| 文件 | 用途 |
|------|------|
| `pipeline/pipeline.py` | 管线主控 |
| `pipeline/config.py` | 管线配置 |
| `pipeline/db.py` | 管线状态 DB |
| `pipeline/spec_engine.py` | Spec 自动生成引擎 |
| `pipeline/qa_standards.py` | QA 标准定义 |
| `pipeline/layers/` | 6 层 + 4 个 L4 子层 |
| `pipeline/executors/` | 执行后端 (local / opencode / dispatch) |

## Infra (集群运维)

| 文件 | 用途 |
|------|------|
| `infra/guardian.py` | 节点健康守护 (自动重启、告警) |
| `infra/monitor.py` | 集群监控 |
| `infra/sync-infra.sh` | 批量同步基础设施到所有节点 |
| `infra/install-agent-daemon.sh` | 安装 agent-daemon 到节点 |
| `infra/snapshot_dispatch_db.py` | DB 快照备份 |
| `infra/oci-arm-grab.sh` | OCI ARM 实例抢占脚本 |
| `infra/*.service` | systemd 服务文件 |

## 环境变量

dispatch.py 支持通过环境变量自定义路径（默认值适用于 Howard 本地）：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DISPATCH_HOME` | `~/Downloads/dispatch` | dispatch 安装目录 (DB, nodes.json 等) |
| `DISPATCH_SPECS` | `~/Downloads/specs` | spec 文件目录 |
| `DISPATCH_PROJECTS` | `~/Downloads` | 项目代码根目录 |

团队成员在网关上已自动配置为 `~/dispatch`, `~/specs`, `~/projects`。

## 支持的 AI 模型

- **GLM** (智谱 via Z.ai) — 主力
- **MiniMax M2.5** — 备用
- **Claude** (Anthropic) — 高级任务
- **Codex** (OpenAI) — 验证任务

## 文档

| 文档 | 说明 |
|------|------|
| [团队快速入门](./docs/TEAM_QUICKSTART.md) | 新成员 5 分钟上手 |
| [搭建指南](./docs/SETUP_ZH.md) | 从零搭建集群 |
| [Spec 编写指南](./docs/SPEC_GUIDE.md) | 怎么写好一个 spec |

## License

MIT
