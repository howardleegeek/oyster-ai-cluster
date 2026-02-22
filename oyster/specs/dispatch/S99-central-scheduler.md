---
task_id: S99-central-scheduler
project: dispatch
priority: 2
depends_on: []
modifies: ["dispatch.py"]
executor: glm
---

## 目标
实现中央调度器：单一进程管理所有项目任务

## 背景
当前每个项目独立运行调度器进程，导致：
- 多个进程占用资源
- 需要手动启动/管理每个项目
- 容易出现僵尸调度器

## 设计方案

### 核心改动

1. **新增 `start-all` 命令**
   ```bash
   python3 dispatch.py start-all  # 启动中央调度器
   ```

2. **schedule_tasks 支持多项目**
   - 当不指定 project 时，查询所有 pending 任务
   - 按 priority + created_at 排序
   - 全局资源分配（所有节点共享）

3. **任务按项目隔离**
   - 每个项目有独立的 spec 目录
   - 任务按 project 字段区分
   - 收集时按项目归档

### 数据结构

```python
# 任务选择逻辑
SELECT * FROM tasks 
WHERE status = 'pending' 
AND depends_on = '[]'  # 或依赖已满足
ORDER BY priority ASC, created_at ASC
LIMIT 10
```

### 优点
- 单进程，低资源
- 自动管理所有项目
- 无需 launchd 守护（自带 --watch）
- 更好的全局负载均衡

### 使用方式

```bash
# 启动中央调度器（推荐）
python3 dispatch.py start-all --watch

# 停止
python3 dispatch.py stop-all
```

## 验收标准
- [ ] `start-all` 命令存在
- [ ] 能调度所有项目的 pending 任务
- [ ] --watch 模式工作正常
