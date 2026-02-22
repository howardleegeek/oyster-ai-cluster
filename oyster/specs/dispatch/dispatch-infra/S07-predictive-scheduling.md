---
task_id: S11-predictive-scheduling
project: dispatch
priority: 2
depends_on: []
modifies:
  - dispatch/predictor.py
  - dispatch/dispatch.py
executor: glm
---

# Predictive Scheduling: 智能预测调度

## 目标
基于历史任务数据，ML 预测任务耗时，提前分配资源，实现最优调度

## 约束
- 不修改现有 dispatch 核心逻辑
- 使用简单线性回归或规则引擎
- 预测结果仅供参考，不强制执行

## 背景
当前 dispatch 是"先来先服务"，不知道任务要跑多久，导致：
- 短任务卡在长任务后面
- 节点空闲不知道该分配什么任务
- 资源利用率低

## 具体改动

### 1. 新增 predictor.py
```python
# 核心功能
class TaskPredictor:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.model = None  # 简单线性回归或规则
    
    def train(self):
        """从 dispatch.db 读取历史数据训练"""
        # 特征: task_id, project, priority, depends_on count, node
        # 目标: duration
    
    def predict(self, task_spec: dict) -> float:
        """预测任务耗时 (秒)"""
        # 输入: spec 文件内容
        # 输出: 预测耗时
    
    def get_optimal_node(self, task_spec: dict, available_nodes: list) -> str:
        """预测 + 负载均衡 = 最优节点"""
```

### 2. 特征工程
| 特征 | 来源 | 权重 |
|------|------|------|
| project 类型 | spec.project | 高 |
| priority | spec.priority | 高 |
| depends_on 数量 | spec.depends_on | 中 |
| 历史同类任务耗时 | dispatch.db | 高 |
| 节点当前负载 | nodes.json | 中 |

### 3. 调度优化策略
```python
def schedule_with_prediction(tasks: list, nodes: list) -> list:
    # 1. 预测每个任务耗时
    for task in tasks:
        task.predicted_duration = predictor.predict(task.spec)
    
    # 2. 按预测耗时排序 (短任务优先)
    tasks.sort(key=lambda t: t.predicted_duration)
    
    # 3. 分配到负载最低的节点
    for task in tasks:
        task.node = find_least_loaded_node(nodes)
    
    return tasks
```

### 4. 数据收集
每次任务完成后，记录:
```python
task_record = {
    "task_id": spec.task_id,
    "project": spec.project,
    "priority": spec.priority,
    "depends_on_count": len(spec.depends_on),
    "node": actual_node,
    "duration": actual_duration,  # 实际耗时
    "success": success_flag
}
```

## 文件清单

| 文件 | 操作 | 描述 |
|------|------|------|
| `dispatch/predictor.py` | 新建 | 预测引擎 (~300行) |
| `dispatch/dispatch.py` | 修改 | 集成预测调度 |

## 验收标准

- [ ] 能从 dispatch.db 读取历史数据
- [ ] 能预测任务耗时 (误差 < 50%)
- [ ] 能找出当前负载最低的节点
- [ ] 调度建议写入日志供参考
- [ ] 预测准确度随数据增加而提升

## 测试命令
```bash
cd ~/Downloads/dispatch
python3 -m pytest tests/test_predictor.py -v
```

## 不要做

- 不强制使用预测结果 (只提供建议)
- 不修改 nodes.json
- 不修改项目配置
- 不删除任何历史数据
