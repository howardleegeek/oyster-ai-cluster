# PROJECT.md — Infra

> Infra 项目定义（系统自维护）

## 项目范围

**系统自维护**: infrastructure 仓库自身的维护、脚本、配置管理

## 重要：对接现有根目录组件

**Infra 项目的特殊性**：

1. **实际执行组件在仓库根目录**：
   - `infrastructure/capabilities.py` — 能力定义
   - `infrastructure/docker-compose.yml` — 容器编排
   - `infrastructure/.env.example` — 环境变量模板
   - `infrastructure/.sops.yaml` — 密钥管理

2. **ai_os/ 只负责任务路由**：
   - 任务追踪：`ai_os/projects/Infra/TASKS.md`
   - 对话日志：`ai_os/projects/Infra/DIALOGUE.md`
   - 记忆存储：`ai_os/projects/Infra/memory/`
   - 产出归档：`ai_os/projects/Infra/outputs/`

3. **不复制不替代**：
   - ai_os/ 不会把根目录文件复制进来
   - 根目录文件的修改必须先写影响分析，等待确认
   - 任务追踪在 ai_os/，执行仍在根目录

## 产出类型

| 类型 | 路径 |
|------|------|
| infra | outputs/infra/ |
| ops | outputs/ops/ |

## 路由说明

- 所有产出必须写入 `ai_os/projects/Infra/outputs/`
- 临时文件放入 `inbox/`
- 归档移到 `archive/`

## 修改根目录前置条件

若需要修改根目录文件（capabilities.py, docker-compose.yml, .env.example, .sops.yaml），**必须**：

1. 写**影响分析**：哪些文件受影响
2. 写**变更计划**：具体改什么
3. **等待确认**：等 Howard 明确同意后才能执行

---

## 关键联系人

- Howard (owner)
