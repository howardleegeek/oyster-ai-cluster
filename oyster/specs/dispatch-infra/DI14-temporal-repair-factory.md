---
task_id: DI14-temporal-repair-factory
project: dispatch-infra
priority: 0
estimated_minutes: 30
depends_on: []
modifies: ["oyster/infra/dispatch/temporal/activities.py"]
executor: glm
---

## 目标

把修理工厂的核心逻辑（repair-strategies.json 匹配 + 策略执行）集成到 Temporal activities.py 的 dispatch_spec 中。当 task 失败时，不再无脑 retry，而是根据失败模式智能应对。

## 背景

当前 297 个 workflow 全部 exit=143 (SIGTERM) 失败后被 Temporal blind retry，每次 retry 用同样的方式再次失败。旧修理工厂在 dispatch-controller.py 里已 disabled。需要把修理逻辑移到 Temporal activity 层。

## 约束

- 读 `oyster/infra/dispatch/repair-strategies.json` 的策略配置（已有）
- 只改 `activities.py`，不改 workflow 逻辑
- 不引入新依赖
- 不重启 dispatch-controller.py

## 实现

### 在 activities.py 顶部加载修理策略

```python
import re

REPAIR_STRATEGIES_FILE = DISPATCH_DIR / "repair-strategies.json"
REPAIR_STRATEGIES = {}
_repair_loaded_at = 0

def _load_repair_strategies():
    """Load repair strategies from JSON (reload every 60s)."""
    global REPAIR_STRATEGIES, _repair_loaded_at
    now = time.time()
    if now - _repair_loaded_at < 60:
        return
    _repair_loaded_at = now
    if REPAIR_STRATEGIES_FILE.exists():
        try:
            data = json.loads(REPAIR_STRATEGIES_FILE.read_text())
            REPAIR_STRATEGIES = data.get("strategies", {})
        except Exception:
            pass

# Node blacklist: node -> unfreeze_time
_node_blacklist: dict[str, float] = {}
BLACKLIST_DURATION = 1800  # 30 minutes
```

### 在 dispatch_spec 中，执行前检查节点黑名单

在 Step 1 (mkdir) 之前：

```python
_load_repair_strategies()

# Check if node is blacklisted by repair factory
if task.node in _node_blacklist:
    if time.time() < _node_blacklist[task.node]:
        remaining = int(_node_blacklist[task.node] - time.time())
        from temporalio.exceptions import ApplicationError
        raise ApplicationError(
            f"Node {task.node} blacklisted by repair factory ({remaining}s remaining)",
            non_retryable=False,
        )
    else:
        del _node_blacklist[task.node]  # Expired, unfreeze
```

### 在 dispatch_spec 中，失败后匹配修理策略

在现有的 retryable error raise 之前（line ~226），加修理逻辑：

```python
# === REPAIR FACTORY: match failure pattern and apply strategy ===
if result.exit_code != 0:
    error_text = f"exit code {result.exit_code} {result.error}"
    matched_strategy = None

    for name, strategy in REPAIR_STRATEGIES.items():
        pattern = strategy.get("pattern", "")
        if pattern and re.search(pattern, error_text, re.IGNORECASE):
            matched_strategy = (name, strategy)
            break

    if matched_strategy:
        sname, sconfig = matched_strategy
        fix = sconfig.get("fix", "retry")
        severity = sconfig.get("severity", "medium")
        diagnosis = sconfig.get("diagnosis", "unknown")

        activity.logger.info(
            f"[{task.task_id}] REPAIR: matched '{sname}' → fix={fix}, "
            f"diagnosis={diagnosis}"
        )

        if fix == "blacklist_node":
            _node_blacklist[task.node] = time.time() + BLACKLIST_DURATION
            activity.logger.warning(
                f"[{task.task_id}] REPAIR: blacklisted {task.node} for {BLACKLIST_DURATION}s"
            )

        elif fix == "cooldown":
            # Rate limited — sleep before retry
            import asyncio
            await asyncio.sleep(30)

        # For all fixes: let Temporal retry handle the rest
        # The blacklist will cause next retry to skip this node
        # (Temporal will pick a different one if workflow supports it)
```

### 修理策略效果

| 失败模式 | pattern | fix | Temporal 行为 |
|----------|---------|-----|--------------|
| exit 143 (killed) | `Terminated\|Killed\|SIGKILL\|SIGTERM` | increase_timeout | retry（下次更长超时） |
| exit 137 (OOM) | `OOM\|out of memory\|exit code 137` | reduce_slots | blacklist node 30min |
| exit 127 (no CLI) | `exit code 127\|command not found` | blacklist_node | blacklist node 30min |
| SSH 失败 | `worker offline\|heartbeat timeout\|Connection refused` | blacklist_node | blacklist node 30min |
| 空输出 | `no output\|empty.*output\|0 files changed` | enrich_prompt | retry（progress.txt 已有上下文） |
| Rate limit | `rate.?limit\|429\|too many requests` | cooldown | sleep 30s 后 retry |
| Git 冲突 | `merge conflict\|CONFLICT` | manual | 标记 non_retryable，不再 retry |

## 验收标准

- [ ] activities.py 启动时加载 repair-strategies.json
- [ ] exit 143 失败匹配 "killed" 策略
- [ ] exit 127 失败后节点被 blacklist 30 分钟
- [ ] blacklisted 节点的下一次 dispatch 抛出 retryable error（Temporal 会重试到其他节点）
- [ ] rate limit 匹配后 sleep 30s 再 retry
- [ ] git conflict 标记为 non_retryable，不再重试
- [ ] 修理日志可见：`[task_id] REPAIR: matched 'xxx' → fix=yyy`

## 不要做

- 不改 workflow 逻辑
- 不重启 dispatch-controller.py
- 不改 repair-strategies.json
- 不加新依赖
- 不要询问是否部署，直接部署
