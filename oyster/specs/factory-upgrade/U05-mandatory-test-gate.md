---
task_id: U05
title: "task-wrapper 强制测试门禁"
depends_on: ["U03"]
modifies: ["dispatch/task-wrapper.sh"]
executor: glm
---

## 目标
Agent 执行完必须跑测试，测试不过 = 任务失败。不允许"跳过测试报完成"。

## 学到的
文章要求：测试不过即判定失败。
我们的问题：Agent 报"Already Complete"但没验证，12/17 个任务声称已修但 58% 测试通过率。

## 改动

### task-wrapper.sh 在 claude 执行完后强制验证

```bash
# === 强制验证阶段 ===
VERIFY_CMD=""

# 1. 优先用 spec 里的 verify 命令
if grep -q "^verify:" "$SPEC_FILE" 2>/dev/null; then
    VERIFY_CMD=$(grep "^verify:" "$SPEC_FILE" | sed 's/^verify: *//' | sed 's/^"//' | sed 's/"$//')
fi

# 2. 否则用项目级测试
if [[ -z "$VERIFY_CMD" ]]; then
    if [[ -f "$WORKING_DIR/Makefile" ]]; then
        VERIFY_CMD="cd $WORKING_DIR && make test"
    elif [[ -f "$WORKING_DIR/package.json" ]]; then
        VERIFY_CMD="cd $WORKING_DIR && npm test"
    elif [[ -f "$WORKING_DIR/backend/requirements.txt" ]]; then
        VERIFY_CMD="cd $WORKING_DIR && python -m pytest backend/tests/ -v --tb=short"
    fi
fi

# 3. 执行验证
if [[ -n "$VERIFY_CMD" ]]; then
    echo "[$(get_timestamp)] Running verification: $VERIFY_CMD"
    eval "$VERIFY_CMD" > "$TASK_DIR/verify.log" 2>&1
    VERIFY_EXIT=$?
    if [[ $VERIFY_EXIT -ne 0 ]]; then
        echo "[$(get_timestamp)] ❌ VERIFICATION FAILED (exit=$VERIFY_EXIT)"
        FINAL_STATUS="failed"
        EXIT_CODE=1
    else
        echo "[$(get_timestamp)] ✅ Verification passed"
    fi
fi

# 4. TODO/FIXME 扫描（已有，改为强制失败而不是警告）
TODO_COUNT=$(grep -rn 'TODO\|FIXME\|HACK\|XXX\|placeholder' "$WORKING_DIR" \
    --include="*.py" --include="*.tsx" --include="*.ts" \
    -l 2>/dev/null | wc -l)
if [[ $TODO_COUNT -gt 0 ]]; then
    echo "[$(get_timestamp)] ⚠️ Found $TODO_COUNT files with TODO/FIXME"
    # 不强制失败，但记录到 status
fi
```

## 验收标准
- [ ] Agent 写完代码后 task-wrapper 自动跑 verify 命令
- [ ] verify 失败 → status.json 写 "failed"
- [ ] dispatch status 能看到哪些任务验证失败了
