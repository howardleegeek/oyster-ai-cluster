---
task_id: S08-hybrid-mode-v2
project: dispatch
priority: 1
depends_on: [S07-pull-mode-v2]
modifies: ["dispatch/task-watcher.py"]
executor: local
---

# S08-hybrid-mode-v2: 混合模式节点执行器

## 目标
节点监听任务目录，自动执行 pending 任务。

## 问题修复
- 路径问题：支持 ~/dispatch/tasks/ 和 ~/dispatch/dispatch/tasks/
- 自动重启：进程退出后自动重启
- 状态同步：执行后更新 status.json

## 实现
```python
# task-watcher.py 功能：
# 1. 扫描任务目录 (5s 间隔)
# 2. 检测 pending 任务
# 3. 执行 wrapper
# 4. 更新 status.json
# 5. 崩溃自动重启
```

## 部署
```bash
# 推送到节点
scp task-watcher.py glm-node-3:~/dispatch/

# 启动
ssh glm-node-3 "DISPATCH_DIR=/home/howardli/dispatch nohup python3 ~/dispatch/task-watcher.py glm-node-3 8 &"
```

## 验收标准
- [ ] 节点检测到 pending 任务自动执行
- [ ] 执行完成后 status 变为 completed/failed
- [ ] 进程崩溃后自动重启
