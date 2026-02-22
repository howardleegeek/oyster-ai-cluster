---
task_id: DI11-node-health-scoring
project: dispatch-infra
priority: 1
estimated_minutes: 45
depends_on: ["DI10-jsonl-metrics-pipeline"]
modifies: ["oyster/infra/dispatch/temporal/activities.py"]
executor: glm
---

## 目标

在 activities.py 中实现节点健康评分（rolling score 0-100），低于 60 的节点自动冻结 30 分钟不派单。

## 背景

当前系统不区分健康和不健康的节点。一个持续失败的节点会不断接收任务，拖累全局吞吐。需要最朴素的信誉机制让系统自愈。

## 约束

- 评分存储: 内存字典 + JSON 持久化到 `~/Downloads/oyster/infra/dispatch/metrics/node_health.json`
- 不改 nodes.json 格式
- 不改 workflow 逻辑（只在 activity 层过滤）
- 不引入新依赖

## 实现

### 1. 新增 `node_health.py` 模块 (新文件，与 activities.py 同目录)

```python
"""Node health scoring — rolling score with freeze threshold."""

import json
import time
from pathlib import Path

HEALTH_FILE = Path.home() / "Downloads/oyster/infra/dispatch/metrics/node_health.json"
FREEZE_DURATION = 1800  # 30 minutes
THRESHOLD = 60
INITIAL_SCORE = 80

# Score adjustments
SCORE_SUCCESS = +2
SCORE_FAILURE = -5
SCORE_TIMEOUT = -8
SCORE_ORPHAN = -15

_scores: dict[str, dict] = {}  # node -> {"score": int, "frozen_until": float}


def _load():
    global _scores
    if not _scores and HEALTH_FILE.exists():
        try:
            _scores = json.loads(HEALTH_FILE.read_text())
        except Exception:
            _scores = {}


def _save():
    HEALTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    HEALTH_FILE.write_text(json.dumps(_scores, indent=2))


def _get(node: str) -> dict:
    _load()
    if node not in _scores:
        _scores[node] = {"score": INITIAL_SCORE, "frozen_until": 0}
    return _scores[node]


def record_result(node: str, exit_code: int):
    """Update node score based on task result."""
    entry = _get(node)
    if exit_code == 0:
        entry["score"] = min(100, entry["score"] + SCORE_SUCCESS)
    elif exit_code in (137, 124):  # timeout/kill
        entry["score"] = max(0, entry["score"] + SCORE_TIMEOUT)
    else:
        entry["score"] = max(0, entry["score"] + SCORE_FAILURE)

    # Freeze if below threshold
    if entry["score"] < THRESHOLD:
        entry["frozen_until"] = time.time() + FREEZE_DURATION

    _save()


def is_available(node: str) -> bool:
    """Check if node is available (not frozen)."""
    entry = _get(node)
    if entry["frozen_until"] > time.time():
        return False
    # Auto-unfreeze expired nodes
    if entry["frozen_until"] > 0 and entry["frozen_until"] <= time.time():
        entry["frozen_until"] = 0
    return True


def get_status() -> dict:
    """Return all node health statuses."""
    _load()
    now = time.time()
    return {
        node: {
            "score": data["score"],
            "frozen": data["frozen_until"] > now,
            "frozen_remaining_s": max(0, int(data["frozen_until"] - now)),
        }
        for node, data in _scores.items()
    }
```

### 2. 修改 activities.py `dispatch_spec`

在 return result 前：

```python
from node_health import record_result, is_available

# Check if node is frozen
if not is_available(task.node):
    from temporalio.exceptions import ApplicationError
    raise ApplicationError(
        f"Node {task.node} frozen (health < 60), retrying on different node",
        non_retryable=False,
    )

# ... (existing execution logic) ...

# After execution, record result
record_result(task.node, result.exit_code)
```

### 3. 恢复规则

连续 5 次成功：score 上升 10 点（5 x +2），自动回到 60 以上。
冻结 30 分钟后自动解冻（`frozen_until` 过期）。

## 验收标准

- [ ] `node_health.json` 在首次 task 完成后自动创建
- [ ] 成功 task 使 score +2，失败 -5，超时 -8
- [ ] score < 60 时节点被标记 frozen，30 分钟内不接新任务
- [ ] frozen 节点的 task 抛出 retryable error，Temporal 会重试到其他节点
- [ ] `get_status()` 可被 Telegram bot 调用展示节点健康

## 不要做

- 不搞复杂的拜占庭容错
- 不改 nodes.json
- 不改 workflow 逻辑
- 不要询问是否部署，直接部署
