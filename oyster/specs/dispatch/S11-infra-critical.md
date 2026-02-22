---
task_id: S11-infra-critical
project: dispatch
priority: 1
depends_on: []
modifies: ["dispatch/guardian.py", "dispatch/task-watcher.py"]
executor: local
---

# S11: 基础设施关键修复

## 问题
1. 节点没有完整代码，任务无法执行
2. task-watcher 停止后不会自动重启
3. dispatch 不会自动同步代码

## 修复

### 1. Guardian C6: 代码同步
```python
def check_code_sync():
    # 检查节点代码是否存在
    # 如果不存在或不最新，执行 rsync
    # 同步 ~/{project}/ 目录
```

### 2. task-watcher 自动重启
- 进程退出时自动重启
- 加 --daemon 模式

### 3. dispatch 启动时 rsync
- deploy_task 前先 rsync 代码
- 或创建预同步任务

## 执行
- 直接修改 guardian.py 加 C6
- 直接修改 task-watcher.py 加 daemon 模式
- 测试验证
