---
executor: glm
task_id: S99-code-queue-infra
project: dispatch
priority: 1
depends_on: []
modifies:
  - pipeline/db.py
  - pipeline/code_queue.py
  - dispatch.py
---
executor: glm

## 目标
为 dispatch 系统增加"代码任务队列"基础设施，支持 24/7 自动写代码。

## 约束
- 不改动现有 runs / layer_results 表结构（向后兼容）
- 新增 code_jobs 表，字段：id, type, source, priority, state, lock_owner, workspace_path, artifact_links, created_at, updated_at
- job.type 分为 `content`（现有）和 `code`（新增）
- 代码不改现有 dispatch.py 核心逻辑，只扩展

## 具体改动

### 1. pipeline/db.py
新增 code_jobs 表：

```python
CREATE TABLE IF NOT EXISTS code_jobs (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK(type IN ('content', 'code')),
    source TEXT NOT NULL CHECK(source IN ('github_issue', 'todo_scan', 'failing_ci', 'manual')),
    priority INTEGER DEFAULT 2,
    state TEXT DEFAULT 'queued' CHECK(state IN ('queued','running','blocked','done','failed','needs_human')),
    lock_owner TEXT,
    lock_expires_at TEXT,
    workspace_path TEXT,
    artifact_links JSON DEFAULT '{}',
    payload JSON,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    error TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 2
);

CREATE INDEX IF NOT EXISTS idx_code_jobs_state ON code_jobs(state);
CREATE INDEX IF NOT EXISTS idx_code_jobs_lock ON code_jobs(lock_owner, lock_expires_at);
```

### 2. pipeline/code_queue.py (新文件)
任务队列核心逻辑：

```python
class CodeQueue:
    """代码任务队列管理器"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
    
    def enqueue(self, job_type: str, source: str, payload: dict, priority: int = 2) -> str:
        """入队，返回 job_id"""
    
    def claim(self, worker_id: str, max_jobs: int = 3) -> List[dict]:
        """worker 认领任务（带锁）"""
    
    def release(self, job_id: str, state: str, error: str = None):
        """释放任务（完成/失败）"""
    
    def get_queued_count(self) -> int:
        """获取排队数量"""
    
    def get_stats(self) -> dict:
        """获取队列统计"""
```

### 3. dispatch.py 扩展
新增 code 相关的子命令：

```python
# python3 dispatch.py code-queue status
# python3 dispatch.py code-queue enqueue --source github_issue --payload '{"issue_id": 123}'
# python3 dispatch.py code-queue claim --worker worker1
# python3 dispatch.py code-queue release <job_id> --state done
```

## 验收标准
- [ ] 新增 code_jobs 表，SQL 可正常执行
- [ ] CodeQueue 类可正常 import 和实例化
- [ ] enqueue → claim → release 流程跑通
- [ ] dispatch.py 新增 code-queue 子命令可用
- [ ] 测试：创建 3 个 job，claim 2 个，release 1 个 done，剩余状态正确

## 验证命令
```bash
cd ~/Downloads/dispatch && python3 -c "
from pipeline.code_queue import CodeQueue
q = CodeQueue()
job_id = q.enqueue('code', 'manual', {'task': 'test'}, priority=1)
print(f'Created job: {job_id}')
jobs = q.claim('worker1', max_jobs=2)
print(f'Claimed: {jobs}')
if jobs:
    q.release(jobs[0]['id'], 'done')
print('Stats:', q.get_stats())
"
```

## 不要做
- 不改现有 L1-L6 层逻辑
- 不改 nodes.json 或 task-wrapper.sh
- 不加认证/API key 逻辑（后续迭代）
