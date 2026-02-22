---
task_id: DI10-jsonl-metrics-pipeline
project: dispatch-infra
priority: 1
estimated_minutes: 30
depends_on: []
modifies: ["oyster/infra/dispatch/temporal/activities.py", "oyster/infra/dispatch/task-wrapper.sh"]
executor: glm
---

## 目标

在 task-wrapper.sh 和 activities.py 中添加 JSONL metrics 记录，使每个 task 完成时写一条 append-only 日志行，支持 24h 窗口指标聚合。

## 背景

当前系统缺少聚合指标。status.json 分散在各 task dir，无法回答"过去 24h 完成了多少 spec"或"成功率是多少"。

## 约束

- JSONL 文件路径: `~/dispatch/metrics/tasks.jsonl`（每个节点本地写）
- Mac-1 聚合路径: `~/Downloads/oyster/infra/dispatch/metrics/tasks.jsonl`（activities.py 写）
- 每条记录一行 JSON，append-only，不锁
- 不改 status.json 格式（保持兼容）
- 不引入新依赖

## 实现

### 1. task-wrapper.sh（节点端，line ~1085 附近，写 status.json 之后）

在写完 status.json 后，追加一行到 `~/dispatch/metrics/tasks.jsonl`：

```bash
mkdir -p "$HOME/dispatch/metrics"
METRICS_LINE="{\"ts\":\"$COMPLETED_AT\",\"task_id\":\"$TASK_ID\",\"project\":\"$PROJECT\",\"node\":\"$NODE\",\"exit_code\":$EXIT_CODE,\"duration_s\":$DURATION,\"attempts\":$ATTEMPT,\"api_mode\":\"$CURRENT_MODE\",\"loc_added\":$LOC_ADDED,\"loc_removed\":$LOC_REMOVED,\"files_changed\":$ARTIFACT_FILES_CHANGED,\"artifact_hash\":\"$ARTIFACT_HASH\"}"
echo "$METRICS_LINE" >> "$HOME/dispatch/metrics/tasks.jsonl"
```

### 2. activities.py（Mac-1 orchestrator 端，dispatch_spec 返回后）

在 `dispatch_spec` activity 的 return 前，追加一行到本地 JSONL：

```python
import json
from pathlib import Path

metrics_dir = Path.home() / "Downloads/oyster/infra/dispatch/metrics"
metrics_dir.mkdir(parents=True, exist_ok=True)
metrics_file = metrics_dir / "tasks.jsonl"

record = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
    "task_id": task.task_id,
    "project": task.project,
    "node": task.node,
    "exit_code": result.exit_code,
    "duration_s": result.duration_seconds,
    "loc_added": result.loc_added,
    "loc_removed": result.loc_removed,
    "files_changed": result.files_changed,
    "error": result.error[:200] if result.error else "",
    "retryable": result.exit_code in {143, 137, 255, 124},
}
with open(metrics_file, "a") as f:
    f.write(json.dumps(record) + "\n")
```

## 验收标准

- [ ] task-wrapper.sh 每次执行完毕后 `~/dispatch/metrics/tasks.jsonl` 多一行
- [ ] activities.py 每次 dispatch_spec 返回后 `~/Downloads/oyster/infra/dispatch/metrics/tasks.jsonl` 多一行
- [ ] JSONL 行格式可用 `python3 -c "import json; [json.loads(l) for l in open('tasks.jsonl')]"` 验证
- [ ] 不影响现有 status.json 写入

## 不要做

- 不搞 OpenTelemetry（那是 S12 的事）
- 不加 rotation/压缩（后续再做）
- 不改 Telegram bot（后续用 JSONL 数据驱动 /status）
- 不要询问是否部署，直接部署
