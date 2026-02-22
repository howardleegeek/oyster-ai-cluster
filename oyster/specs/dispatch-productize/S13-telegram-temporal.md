---
task_id: S13-telegram-temporal
project: dispatch-productize
priority: 1
estimated_minutes: 30
depends_on: []
modifies: ["oyster/infra/dispatch/pipeline/telegram_bot_final.py"]
executor: glm
---

## 目标

将 Telegram Bot 的数据源从 SQLite 切换到 Temporal API，保持所有命令和 UI 不变。

## 实现

### 1. 添加 Temporal client 初始化

```python
from temporalio.client import Client

TEMPORAL_HOST = os.environ.get("TEMPORAL_HOST", "localhost:7233")

# 在 main() 中初始化，存到 application.bot_data
async def post_init(application):
    application.bot_data["temporal"] = await Client.connect(TEMPORAL_HOST)
```

### 2. 替换命令数据源

| 命令 | 现在 (SQLite) | 改成 (Temporal) |
|------|--------------|----------------|
| `/status` | `SELECT count(*) FROM tasks GROUP BY status` | `client.list_workflows()` 按状态统计 |
| `/nodes` | `SELECT DISTINCT node FROM tasks` | `client.list_workflows()` 提取 worker identity |
| `/pipeline` | `SELECT * FROM tasks WHERE status='running'` | `client.list_workflows(query="ExecutionStatus='Running'")` |
| `/failed` | `SELECT * FROM tasks WHERE status='failed'` | `client.list_workflows(query="ExecutionStatus='Failed'")` |
| `/project X` | `SELECT * FROM tasks WHERE project=?` | `client.list_workflows(query="WorkflowId STARTS_WITH 'project-X'")` |
| `/report` | 聚合 SQLite 数据 | 从 workflow result 读取 |

### 3. 保持双模式兼容

```python
USE_TEMPORAL = os.environ.get("USE_TEMPORAL", "false").lower() == "true"

async def get_task_stats(bot_data):
    if USE_TEMPORAL:
        client = bot_data["temporal"]
        # ... Temporal API
    else:
        # ... 原有 SQLite 逻辑不动
```

### 4. 新增 Temporal 专属命令

- `/workflow <id>` — 查看 workflow 详情和历史
- `/workers` — 列出所有连接的 worker 和负载

## 约束

- 不改现有命令的输出格式
- SQLite 模式保留为 fallback (USE_TEMPORAL=false)
- 不改 bot token / 权限 / 其他配置
- pip install temporalio 到 bot 运行环境

## 验收标准

- [ ] USE_TEMPORAL=true 时所有命令正常工作
- [ ] USE_TEMPORAL=false 时行为不变
- [ ] `/status` 显示 Temporal workflow 统计
- [ ] `/pipeline` 显示 running workflows
- [ ] `/failed` 显示失败的 workflows

## 不要做

- 不改 bot 的 UI/消息格式
- 不改认证/权限逻辑
- 不删除 SQLite 相关代码
