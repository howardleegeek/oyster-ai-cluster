---
task_id: DI07-github-artifact-archive
project: dispatch-infra
priority: 0
estimated_minutes: 40
depends_on: []
modifies: ["task-wrapper.sh"]
executor: glm
---
## 目标
任务完成后，自动将 output/ 和关键结果 push 到 GitHub 仓库，然后删除本地文件，防止节点磁盘爆满。

## 技术方案
在 task-wrapper.sh 的任务完成后（cleanup_task 之前）添加：

```bash
archive_to_github() {
    local task_dir="$1"
    local project="$2"
    local task_id="$3"

    # Only archive if task succeeded (exit code 0)
    if [ "$TASK_EXIT_CODE" -ne 0 ]; then
        echo "[archive] Skipping archive for failed task"
        return 0
    fi

    # Check if output dir has content
    if [ ! -d "$task_dir/output" ] || [ -z "$(ls -A "$task_dir/output" 2>/dev/null)" ]; then
        echo "[archive] No output to archive"
        return 0
    fi

    # Create a temporary git repo for the archive
    local archive_dir="/tmp/archive-${task_id}"
    mkdir -p "$archive_dir"
    cp -r "$task_dir/output" "$archive_dir/"
    cp "$task_dir/status.json" "$archive_dir/" 2>/dev/null
    cp "$task_dir/task.log" "$archive_dir/" 2>/dev/null

    cd "$archive_dir"
    git init
    git add -A
    git commit -m "Archive: ${project}/${task_id} $(date -u +%Y%m%d-%H%M)"

    # Push to project's archive branch
    local repo_url="https://github.com/howardleegeek/${project}.git"
    git push "$repo_url" HEAD:refs/heads/archive/${task_id} --force 2>/dev/null || {
        echo "[archive] Push failed, keeping local files"
        rm -rf "$archive_dir"
        return 1
    }

    echo "[archive] Pushed to ${repo_url} branch archive/${task_id}"
    rm -rf "$archive_dir"
    return 0
}
```

## 约束
- 修改现有 task-wrapper.sh
- 只在任务成功 (exit code 0) 时 archive
- Push 失败时保留本地文件（不丢数据）
- 使用 archive/ 分支前缀，不污染 main
- 不改任务执行逻辑
- 不改 dispatch-controller.py

## 验收标准
- [ ] 成功任务的 output/ 被 push 到 GitHub
- [ ] 使用 archive/{task_id} 分支
- [ ] push 成功后本地 output/ 被 cleanup_task 删除
- [ ] push 失败时本地文件保留
- [ ] 不影响任务执行流程

## 不要做
- 不改任务执行逻辑
- 不改 dispatch-controller.py
- 不 push 到 main 分支
- 不 archive 失败的任务
