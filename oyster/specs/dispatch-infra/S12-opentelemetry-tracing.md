---
task_id: S12-opentelemetry-tracing
project: dispatch-infra
priority: 2
estimated_minutes: 30
depends_on: []
modifies: ["task-wrapper.sh"]
executor: glm
---

## 目标
仅修改 task-wrapper.sh，添加结构化 JSON 日志输出（trace.jsonl）。不碰 Python 文件。

## 背景
排查问题需要 SSH 到各节点 grep task.log，格式不统一。添加结构化 trace.jsonl 作为第一步。

## 改动范围 — 只改 task-wrapper.sh，只加一个函数 + 三行调用

### 唯一改动: task-wrapper.sh 添加 log_json 函数

在 task-wrapper.sh 文件顶部（shebang 之后、任何逻辑之前）添加:
```bash
log_json() {
    local level="$1" event="$2" msg="$3"
    echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"level\":\"$level\",\"event\":\"$event\",\"task_id\":\"${TASK_ID:-unknown}\",\"node\":\"$(hostname)\",\"msg\":\"$msg\"}" >> "${TASK_DIR:-.}/trace.jsonl"
}
```

然后在现有代码的三个位置插入调用（不删除不修改任何现有代码行）:
1. 任务开始时（在现有 echo 或 log 行之后）: `log_json "INFO" "task.start" "开始执行 $TASK_ID"`
2. 任务成功完成时: `log_json "INFO" "task.complete" "任务完成 exit=$EXIT_CODE"`
3. 任务失败时: `log_json "ERROR" "task.fail" "执行失败 exit=$EXIT_CODE"`

## 绝对禁止
- ❌ 不碰 dispatch-controller.py（任何修改都判 FAIL）
- ❌ 不碰 dispatch.py（任何修改都判 FAIL）
- ❌ 不碰 bootstrap.sh
- ❌ 不加任何 Python 依赖（opentelemetry 等）
- ❌ 不加任何 HTTP endpoint
- ❌ 不加任何新文件（除 trace.jsonl 由运行时产生）
- ❌ 不删除 task-wrapper.sh 中任何现有代码行
- ❌ 不改变 task-wrapper.sh 的现有行为（exit code、task.log 输出等）

## 验收标准
- [ ] task-wrapper.sh 有 log_json 函数定义
- [ ] 执行后 $TASK_DIR/trace.jsonl 有 task.start 行（JSON 格式）
- [ ] 成功时有 task.complete 行，失败时有 task.fail 行
- [ ] 现有 task.log 行为完全不变
- [ ] dispatch-controller.py 和 dispatch.py 文件零改动
- [ ] bash -n task-wrapper.sh 语法检查通过
