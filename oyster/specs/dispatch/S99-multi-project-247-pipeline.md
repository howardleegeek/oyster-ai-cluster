---
task_id: S99-multi-project-247-pipeline
project: dispatch
priority: 1
depends_on: [S99-scheduler-cluster]
modifies:
  - pipeline/projects.yaml
  - pipeline/scheduler.py
  - pipeline/self_healer.py
executor: glm
---

## 目标
把 ClawMarketing, GEM Platform, Infrastructure 接入 24/7 自动写代码 pipeline，并配置自我修复机制。

## 约束
- 复用现有 projects.yaml 配置
- 不改动现有项目代码结构
- 24/7 运行，核心原则：不能停

## 具体改动

### 1. pipeline/projects.yaml
添加 oyster-infra 项目：

```yaml
  oyster-infra:
    path: ~/Downloads/infrastructure/
    stack: terraform-python
    deploy: terraform
    backend:
      path: ai_os/
      cmd: "python3 -m uvicorn main:app --host 0.0.0.0"
      port: 8000
    env_required: [AWS_ACCESS_KEY, AWS_SECRET_KEY, GCP_PROJECT]
```

### 2. 配置多项目 24/7 调度
修改 scheduler 支持多项目并行：

```python
# projects 配置
PROJECTS = [
    "clawmarketing",
    "gem-platform", 
    "oyster-infra",
    "dispatch"
]
```

### 3. pipeline/self_healer.py (新文件)
自动修复机制：

```python
class SelfHealer:
    """自我修复系统"""
    
    # 健康检查项
    HEALTH_CHECKS = [
        "scheduler_running",
        "queue_not_blocked", 
        "nodes_online",
        "db_responsive",
        "cron_active"
    ]
    
    def check_health(self) -> HealthReport:
        """健康检查"""
    
    def auto_fix(self, issue: str) -> FixResult:
        """自动修复"""
    
    def restart_dispatch(self):
        """重启 dispatch"""
    
    def reset_stuck_jobs(self):
        """重置卡住的任务"""
    
    def alert_on_failure(self, error: str):
        """失败告警"""
```

### 4. 修改 cron 为 24/7
每 5 分钟运行一次（不只在夜间）：

```python
# scheduler.py 修改
CI_SCAN_INTERVAL = 300  # 5 分钟
BATCH_SCAN_INTERVAL = 600  # 10 分钟
```

## 验收标准
- [ ] oyster-infra 项目添加到 projects.yaml
- [ ] 多项目可并行调度
- [ ] SelfHealer 可检测并修复常见问题
- [ ] Cron 改为 24/7 运行
- [ ] 监控系统就绪

## 验证命令
```bash
cd ~/Downloads/dispatch && python3 -c "
from pipeline.self_healer import SelfHealer
healer = SelfHealer()
report = healer.check_health()
print('Health:', report)
"
```
