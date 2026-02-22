---
task_id: S99-scheduler-cluster
project: dispatch
priority: 1
depends_on: [S99-night-shift-scheduler]
modifies:
  - pipeline/scheduler.py
  - pipeline/cluster_runner.py
executor: glm
---

## 目标
让 NightShiftScheduler 可以在集群节点上分布式运行，利用全部 145 slots。

## 约束
- 复用现有 nodes.json 节点配置
- 复用 dispatch.py 的 SSH 执行机制
- 不改动 nodes.json
- 支持任务级联失败自动换节点

## 具体改动

### 1. pipeline/cluster_runner.py (新文件)
```python
class ClusterRunner:
    """集群任务运行器"""
    
    def __init__(self, nodes_config: str = None):
        self.nodes = self._load_nodes(nodes_config)
    
    def get_available_nodes(self) -> List[dict]:
        """获取可用节点（按优先级排序）"""
    
    def run_on_node(self, node: dict, command: str) -> ExecResult:
        """在指定节点运行命令"""
    
    def dispatch_job(self, job: dict, worker_id: str) -> DispatchResult:
        """分配任务到最佳节点"""
    
    def wait_for_completion(self, dispatch_id: str, timeout: int) -> JobResult:
        """等待任务完成"""
```

### 2. pipeline/scheduler.py 扩展
```python
class NightShiftScheduler:
    # 新增
    def __init__(self, queue, cluster_runner=None):
        self.queue = queue
        self.cluster = cluster_runner or ClusterRunner()
    
    def dispatch_job_to_cluster(self, job: dict) -> str:
        """分配任务到集群节点"""
    
    def check_cluster_results(self) -> List[JobResult]:
        """检查集群任务结果"""
    
    def run_batch_distributed(self, worker_id: str, max_jobs: int) -> BatchResult:
        """分布式批量运行"""
```

## 验收标准
- [ ] 可加载 nodes.json 配置
- [ ] 可 SSH 到远程节点执行命令
- [ ] 任务自动分配到空闲节点
- [ ] 支持 slot 管理（不超限）
- [ ] 支持失败自动重试其他节点

## 验证命令
```bash
cd ~/Downloads/dispatch && python3 -c "
from pipeline.cluster_runner import ClusterRunner
runner = ClusterRunner()
nodes = runner.get_available_nodes()
print(f'Available nodes: {len(nodes)}')
for n in nodes[:3]:
    print(f'  - {n[\"name\"]}: {n[\"slots\"]} slots')
"
```
