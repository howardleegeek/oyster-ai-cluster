---
task_id: DI06-spec-quality-gate
project: dispatch-infra
priority: 2
estimated_minutes: 25
depends_on: []
modifies: ["task-wrapper.sh"]
executor: glm
---
## 目标
在 task-wrapper.sh 的 spec 传递中，强制添加 "MUST write code" 提醒，减少 Gate 2 failures

## 技术方案
在 task-wrapper.sh 构建 spec 内容传给 opencode 之前，追加一段强制提醒：

```bash
# Append critical reminder to spec content
SPEC_CONTENT=$(cat "$SPEC_FILE")
CRITICAL_REMINDER="

【CRITICAL REMINDER】You MUST use apply_patch/write_file/edit_file tools to actually CREATE or MODIFY files. Do NOT just describe changes in text. If you only output text without tool calls, the task will FAIL. Start by reading the relevant files, then immediately write/edit them."

FULL_SPEC="${SPEC_CONTENT}${CRITICAL_REMINDER}"
```

## 约束
- 修改现有 task-wrapper.sh
- 只在传给 opencode 的 spec 内容后追加提醒
- 不修改原始 spec 文件
- 提醒文字简短但强制

## 验收标准
- [ ] opencode 收到的 spec 末尾有 CRITICAL REMINDER
- [ ] 原始 spec.md 文件不被修改
- [ ] 所有任务都会有这个提醒

## 不要做
- 不改 spec 文件本身
- 不改 opencode 命令行参数
- 不改 dispatch-controller.py
