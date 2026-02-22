---
task_id: S08-cleanup-redundancy
project: dispatch-productize
priority: 1
estimated_minutes: 60
depends_on: ["S03-migrate-core-daemons"]
modifies: ["oyster/infra/dispatch/guardian.py", "oyster/infra/dispatch/dispatch.py"]
executor: glm
---

## 目标

清理冗余代码：统一为 Pull 模式为主 + Push 为备用，删除重复功能。

## 背景

当前系统有以下冗余：
1. Pull（controller heartbeat）和 Push（dispatch.py SSH）两套并行
2. Guardian SSH 健康检查 与 Controller heartbeat 离线检测重复
3. 进程管理有 launchd + nonstop-loop.sh + worker-watchdog.sh 三套
4. dispatch.py 中有大量注释掉的旧代码

## 实现

### 1. 统一健康检测
- Guardian 删除 SSH 健康检查逻辑（check_ssh_connection、check_node_availability）
- 改为查询 controller `/v1/workers` API 获取节点状态
- 保留 Guardian 的 DB schema 检查、code sync、stuck task 检测

### 2. 统一进程管理
- 保留 launchd plist 作为 supervisor.py 的守护
- supervisor.py 管理 guardian/reaper/factory/controller
- 删除 nonstop-loop.sh、worker-watchdog.sh

### 3. 标记 Push 为 fallback
- dispatch.py SSH 部署逻辑保留但标记为 `DEPLOY_MODE=ssh`（fallback）
- 默认使用 controller HTTP 部署（`DEPLOY_MODE=http`）
- 环境变量切换

### 4. 清理死代码
- 删除注释掉的旧代码块
- 删除未使用的 import
- 删除 .bak 文件（dispatch.py.bak, task-wrapper.sh.bak 等）

## 约束

- 不删功能，只合并重复的
- Push SSH 保留为 fallback，不完全删除
- 每次删除前确认代码确实未使用

## 验收标准

- [ ] Guardian 不再直接 SSH 到节点（通过 controller API）
- [ ] nonstop-loop.sh 和 worker-watchdog.sh 已删除
- [ ] .bak 文件已删除
- [ ] `grep -r '# TODO\|# HACK\|# FIXME' dispatch/ | wc -l` 减少
- [ ] 所有 daemon 正常运行

## 不要做

- 不删除 Push SSH 功能（保留为 fallback）
- 不改 controller API
- 不改 task-wrapper.sh
