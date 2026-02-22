# Dispatch Registry — 跨 Session/节点 任务去重

## 问题

当前 dispatch 脚本 (dispatch_node1.sh, dispatch_mac2.sh, dispatch_node2.sh) 各自硬编码任务列表，
不同 Opus session 或并行脚本之间没有共享状态，导致：
1. 同一任务被多个节点/session 重复 dispatch
2. 无法准确判断全局进度
3. 失败任务没有自动重试/重新分配

## 方案: 文件锁 dispatch registry

### 核心文件

```
~/Downloads/dispatch-registry.json   # Mac-1 主副本 (source of truth)
```

### Schema

```json
{
  "version": 1,
  "updated_at": "2026-02-11T22:00:00-08:00",
  "tasks": {
    "S01": {
      "status": "completed",
      "node": "mac2",
      "pid": 9341,
      "started_at": "2026-02-11T22:12:52-08:00",
      "completed_at": "2026-02-11T22:35:00-08:00",
      "log": "~/clawmarketing-logs/S01.log"
    },
    "S08": {
      "status": "running",
      "node": "codex-node-1",
      "pid": 12345,
      "started_at": "2026-02-11T22:12:52-08:00"
    },
    "S15": {
      "status": "pending"
    }
  }
}
```

status 枚举: `pending | claimed | running | completed | failed`

### 操作协议

**dispatch 前 (claim)**:
```bash
# 1. 读 registry
# 2. 检查目标任务 status
#    - pending → 写 status=claimed, node=self, ts=now → 继续 dispatch
#    - claimed/running → 跳过 (别人在做)
#    - completed → 跳过
#    - failed → 可以重试: 写 status=claimed
# 3. 写回 registry (用 flock 防并发)
```

**dispatch 后 (update)**:
```bash
# 启动成功 → status=running, pid=<pid>
# 执行完成 → status=completed, completed_at=now
# 执行失败 → status=failed, error=<msg>
```

### 实现: dispatch_with_registry.sh

替代现有的 dispatch_*.sh，所有节点使用同一个脚本，通过参数指定任务:

```bash
#!/bin/bash
# 用法: dispatch_with_registry.sh [S01 S02 ...] 或不带参数执行所有 pending
# 环境变量:
#   REGISTRY=~/Downloads/dispatch-registry.json (默认)
#   NODE_NAME=$(hostname -s)
#   API_MODE=direct|zai (默认 direct)
```

**关键逻辑**:
1. `claim_task()` — flock + jq 原子操作: pending→claimed
2. `run_task()` — 执行 claude -p, 更新 running→completed/failed
3. `main loop` — 遍历参数或所有 pending 任务, 先 claim 再 run

### 远程节点同步

GCP 节点不能直接读 Mac-1 的 registry 文件。两种方案:

**方案 A (推荐): rsync 轮询**
```bash
# 每个远程节点 cron 每 30 秒 sync
rsync -az mac1:~/Downloads/dispatch-registry.json ~/dispatch-registry.json
# 操作后 push 回去
rsync -az ~/dispatch-registry.json mac1:~/Downloads/dispatch-registry.json
```

**方案 B: SSH 直读**
```bash
# claim 时直接 SSH 操作 Mac-1 上的文件
ssh mac1 "flock /tmp/dispatch.lock jq '.tasks.S08.status=\"claimed\"' ~/Downloads/dispatch-registry.json > /tmp/reg.tmp && mv /tmp/reg.tmp ~/Downloads/dispatch-registry.json"
```

选 A，因为网络断开时本地有缓存，不会卡住。

### 对 Opus session 的规则

Opus session 在 dispatch 前 **必须** 先读 registry:
```
1. 读 ~/Downloads/dispatch-registry.json
2. 只 dispatch status=pending 或 status=failed 的任务
3. dispatch 后更新 registry
4. 不要 dispatch status=running 或 status=completed 的任务
```

### 初始化脚本

```bash
#!/bin/bash
# init_registry.sh — 从 specs 目录自动生成 registry
SPECS_DIR=~/Downloads/specs/clawmarketing
REGISTRY=~/Downloads/dispatch-registry.json

echo '{"version":1,"updated_at":"'$(date -Iseconds)'","tasks":{' > "$REGISTRY"
first=true
for spec in "$SPECS_DIR"/S*.md; do
    name=$(basename "$spec" .md | cut -d'-' -f1) # S01, S02...
    if [ "$first" = true ]; then first=false; else echo ',' >> "$REGISTRY"; fi
    echo "\"$name\":{\"status\":\"pending\",\"spec\":\"$(basename $spec)\"}" >> "$REGISTRY"
done
echo '}}' >> "$REGISTRY"
```

### 状态查看

```bash
# 快速查看
jq '.tasks | to_entries | group_by(.value.status) | map({status: .[0].value.status, count: length, tasks: [.[].key]})' ~/Downloads/dispatch-registry.json

# 一行 summary
jq -r '.tasks | to_entries | group_by(.value.status) | map(.[0].value.status + ": " + (length|tostring)) | join(" | ")' ~/Downloads/dispatch-registry.json
```

## 执行者

- **实现脚本**: GLM (dispatch_with_registry.sh + init_registry.sh)
- **部署到节点**: Codex 副元帅 (SCP + 配置)
- **Opus**: 只写这个 spec，不写代码

## 验收标准

1. `dispatch-registry.json` 被正确初始化
2. 两个并发 dispatch 进程不会 claim 同一个任务
3. `jq` status 查询能正确显示全局进度
4. 远程节点 rsync 同步正常工作
