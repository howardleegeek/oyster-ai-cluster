---
task_id: DI03-task-cleanup-post-complete
project: dispatch-infra
priority: 1
estimated_minutes: 25
depends_on: []
modifies: ["task-wrapper.sh"]
executor: glm
---
## 目标
在 task-wrapper.sh 中添加任务完成后的自动清理逻辑，防止节点 disk 爆满

## 技术方案
在 task-wrapper.sh 的最后（任务完成后，无论成功或失败）添加清理逻辑：

```bash
cleanup_task() {
    local task_dir="$1"
    # Remove the cloned repo (biggest space consumer)
    if [ -d "$task_dir/repo" ]; then
        local repo_size=$(du -sh "$task_dir/repo" 2>/dev/null | cut -f1)
        rm -rf "$task_dir/repo"
        echo "Cleaned up repo dir ($repo_size)"
    fi
    # Remove node_modules if present
    find "$task_dir" -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null
    # Remove .git if present (keep output artifacts only)
    find "$task_dir" -name ".git" -type d -exec rm -rf {} + 2>/dev/null
    # Keep: output/, status.json, task.log, spec.md, wrapper.log
}

# Call at exit
trap 'cleanup_task "$TASK_DIR"' EXIT
```

## 约束
- 修改现有 task-wrapper.sh，不新建文件
- 只清理 repo clone 和大文件（node_modules, .git）
- 保留 output/、status.json、task.log、spec.md（需要回传）
- 用 trap EXIT 确保即使任务失败也会清理
- 不改任务执行逻辑

## 验收标准
- [ ] 任务完成后 repo/ 目录被删除
- [ ] node_modules/ 被清理
- [ ] output/ 和 status.json 保留
- [ ] 即使任务 exit code != 0 也会清理

## 不要做
- 不改任务执行逻辑
- 不删 output/ 目录
- 不改 dispatch-controller.py
