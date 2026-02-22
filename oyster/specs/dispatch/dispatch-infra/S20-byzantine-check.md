---
task_id: S20-byzantine-check
project: dispatch-infra
priority: 1
depends_on: []
modifies:
  - dispatch/byzantine_fixer.py
executor: glm
---

# Byzantine Analysis & Fix: 系统一致性检查

## 目标
检测并修复 dispatch 系统的拜占庭问题（不一致状态、孤立数据、时间戳缺失等）

## 问题列表

### 当前发现的问题

| # | 问题类型 | 数量 | 状态 |
|---|---------|------|------|
| 1 | 孤立任务 (无 project) | 0 | ✅ |
| 2 | 重复任务 ID | 0 | ✅ |
| 3 | 卡住任务 (>24h) | 0 | ✅ |
| 4 | 运行中但无节点 | 0 | ✅ |
| 5 | 已完成但无时间戳 | 4 | ⚠️ |
| 6 | 负 slots 节点 | 0 | ✅ |
| 7 | 陈旧文件锁 (>24h) | 0 | ✅ |

### 需要修复的已完成任务（无时间戳）
- S21-infra-backend-setup
- S601-vault-physical-storage
- S02-agent-self-evolve
- S19-agent-teams-integration

## 具体改动

### 1. 新增 byzantine_fixer.py
```python
class ByzantineFixer:
    """检测并修复系统不一致问题"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def check_all(self) -> dict:
        """执行全部检查"""
        return {
            "orphaned_tasks": self.find_orphaned_tasks(),
            "duplicate_ids": self.find_duplicates(),
            "stuck_tasks": self.find_stuck_tasks(),
            "running_without_node": self.find_running_without_node(),
            "completed_without_time": self.find_completed_without_time(),
            "negative_slots": self.find_negative_slots(),
            "stale_locks": self.find_stale_locks(),
        }
    
    def fix_completed_without_timestamp(self):
        """修复已完成但无时间戳的任务"""
        # 如果有 started_at，使用 started_at + 平均任务时长
        # 否则使用当前时间
    
    def fix_stale_locks(self, hours: int = 24):
        """清理陈旧文件锁"""
    
    def generate_report(self) -> str:
        """生成拜占庭分析报告"""
```

### 2. 检查项详细说明

```python
def find_orphaned_tasks(self):
    """无 project 的任务"""
    # SELECT id FROM tasks WHERE project IS NULL OR project = ''

def find_duplicates(self):
    """重复 ID"""
    # SELECT id, COUNT(*) FROM tasks GROUP BY id HAVING COUNT(*) > 1

def find_stuck_tasks(self, hours: int = 24):
    """卡住的任务 (>24h)"""
    # status = 'running' AND (now - started_at) > 24h

def find_running_without_node(self):
    """运行中但无节点"""
    # status = 'running' AND (node IS NULL OR node = '')

def find_completed_without_time(self):
    """已完成但无完成时间"""
    # status = 'completed' AND (completed_at IS NULL OR completed_at = '')

def find_negative_slots(self):
    """负 slots 节点"""
    # SELECT name, slots FROM nodes WHERE slots < 0

def find_stale_locks(self, hours: int = 24):
    """陈旧文件锁"""
    # locked_at < now - 24h
```

### 3. 自动修复策略
```python
def auto_fix(self):
    """自动修复"""
    # 1. completed_without_time → 使用当前时间
    # 2. stale_locks → 删除锁记录
    # 3. stuck_tasks → 标记为 failed + error='byzantine_timeout'
```

## 文件清单

| 文件 | 操作 | 描述 |
|------|------|------|
| `dispatch/byzantine_fixer.py` | 新建 | 拜占庭检查和修复 |

## 验收标准

- [ ] 能检测 7 种拜占庭问题
- [ ] 能自动修复时间戳缺失
- [ ] 能清理陈旧文件锁
- [ ] 能报告系统健康状态
- [ ] 不破坏正常数据

## 不要做

- ❌ 不删除任务记录
- ❌ 不修改成功完成的任务时间戳
- ❌ 不修改节点配置
