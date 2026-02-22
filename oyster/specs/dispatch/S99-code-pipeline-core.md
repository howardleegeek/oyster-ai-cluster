---
executor: glm
task_id: S99-code-pipeline-core
project: dispatch
priority: 1
depends_on: [S99-code-queue-infra]
modifies:
  - pipeline/code_pipeline.py
  - pipeline/agents/code_scout.py
  - pipeline/agents/planner.py
  - pipeline/agents/coder.py
---
executor: glm

## 目标
实现 Code Pipeline 核心闭环：`SCOUT → PLANNER → CODER`，支持 24/7 自动写代码。

## 约束
- 复用现有的 CodeQueue (S99-code-queue-infra)
- 分级调度：SCOUT/PLANNER 用轻量模型，CODER 用强模型
- 不改现有 L1-L6 层逻辑
- 任务输出格式标准化

## 具体改动

### 1. pipeline/agents/code_scout.py (新文件)
自动拉取任务来源：

```python
class CodeScout:
    """从 GitHub Issues / CI 失败 / TODO 拉取任务"""
    
    def scan_github_issues(self, repo: str, labels: list = None) -> List[dict]:
        """扫描 GitHub Issues"""
    
    def scan_failing_ci(self, repo: str) -> List[dict]:
        """扫描 CI 失败的任务"""
    
    def scan_todos(self, repo: str) -> List[dict]:
        """扫描代码中的 TODO"""
    
    def should_autofix(self, issue: dict) -> bool:
        """判断是否适合自动修复"""
```

### 2. pipeline/agents/planner.py (新文件)
任务拆解：

```python
class Planner:
    """把任务拆成可执行 spec + 验收标准"""
    
    def decompose(self, task: dict, repo_path: str) -> Plan:
        """生成执行计划"""
    
    def generate_spec(self, task: dict, plan: Plan) -> str:
        """生成 YAML spec"""
    
    def estimate_difficulty(self, task: dict) -> str:
        """评估难度：simple/medium/hard"""
```

### 3. pipeline/agents/coder.py (新文件)
执行代码修改：

```python
class Coder:
    """执行代码修改"""
    
    def apply_spec(self, spec_path: str, workspace: str) -> ExecResult:
        """应用 spec 改代码"""
    
    def run_tests(self, workspace: str, test_cmd: str) -> TestResult:
        """运行测试"""
    
    def rollback(self, workspace: str, changes: list):
        """回滚改动"""
```

### 4. pipeline/code_pipeline.py (新文件)
Pipeline 编排：

```python
class CodePipeline:
    """Code Pipeline 主编排器"""
    
    def __init__(self, queue: CodeQueue):
        self.queue = queue
    
    def run_cycle(self, worker_id: str) -> dict:
        """运行一个完整的 cycle:
        1. SCOUT 拉任务
        2. PLANNER 拆解
        3. CODER 执行
        4. 入队等待测试
        """
    
    def run_forever(self, worker_id: str, max_jobs: int = None):
        """持续运行直到被中断"""
```

## 验收标准
- [ ] CodeScout 可扫描 GitHub Issues
- [ ] Planner 可生成有效 spec
- [ ] Coder 可执行代码修改
- [ ] CodePipeline.run_cycle() 完整闭环可跑通
- [ ] 单元测试通过

## 验证命令
```bash
cd ~/Downloads/dispatch && python3 -c "
from pipeline.code_pipeline import CodePipeline
from pipeline.code_queue import CodeQueue

# 初始化
q = CodeQueue()
pipeline = CodePipeline(q)

# 入队一个测试任务
job_id = q.enqueue('code', 'manual', {
    'repo': 'test-repo',
    'task': 'add logging',
    'file': 'test.py'
}, priority=1)

# 运行一个 cycle
result = pipeline.run_cycle('test-worker')
print('Cycle result:', result)
"
```

## 不要做
- 不做 PR 创建（后续迭代）
- 不做 CI 集成（后续迭代）
- 不做质量门禁（后续迭代）
