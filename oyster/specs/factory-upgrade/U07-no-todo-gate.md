---
task_id: U07
title: "禁止 TODO/placeholder 门禁"
depends_on: []
modifies: ["dispatch/task-wrapper.sh"]
executor: glm
---

## 目标
Agent 产出的代码中如果包含新增的 TODO/FIXME/placeholder，任务标记为 failed。

## 学到的
文章要求：不要用 TODO 糊弄，不要只给伪代码。
我们的问题：GLM agent 经常输出 # TODO: implement 就报完成。

## 改动

### task-wrapper.sh 在执行后对比新增的 TODO

```bash
# 执行前记录已有 TODO
TODO_BEFORE=$(grep -rn 'TODO\|FIXME\|HACK\|placeholder' "$WORKING_DIR" \
    --include="*.py" --include="*.tsx" --include="*.ts" 2>/dev/null | wc -l)

# ... claude 执行 ...

# 执行后检查新增 TODO
TODO_AFTER=$(grep -rn 'TODO\|FIXME\|HACK\|placeholder' "$WORKING_DIR" \
    --include="*.py" --include="*.tsx" --include="*.ts" 2>/dev/null | wc -l)

NEW_TODOS=$((TODO_AFTER - TODO_BEFORE))
if [[ $NEW_TODOS -gt 0 ]]; then
    echo "[$(get_timestamp)] ❌ Agent added $NEW_TODOS new TODO/FIXME — REJECTED"
    grep -rn 'TODO\|FIXME\|HACK\|placeholder' "$WORKING_DIR" \
        --include="*.py" --include="*.tsx" --include="*.ts" 2>/dev/null | tail -10
    FINAL_STATUS="failed"
    EXIT_CODE=1
fi
```

## 验收标准
- [ ] Agent 新增 TODO → 任务 failed
- [ ] 已有 TODO 不触发（只检查增量）
