---
executor: glm
task_id: S99-night-shift-scheduler
project: dispatch
priority: 2
depends_on: [S99-code-pipeline-core]
modifies:
  - pipeline/scheduler.py
  - pipeline/crontab.py
---
executor: glm

## 目标
实现夜间自动调度器：定时触发 + CI 失败即时响应 + 保险丝控制。

## 约束
- 夜间批量: 1:00-6:00
- CI 失败扫描: 每 15 分钟
- 保险丝: 每晚最多 5 个 PR，每个 repo 最多 2 并发
- 高风险文件自动 needs_human

## 具体改动

### pipeline/scheduler.py (新文件)
```python
class NightShiftScheduler:
    """夜间调度器"""
    
    # 保险丝配置
    MAX_PRS_PER_NIGHT = 5
    MAX_CONCURRENT_PER_REPO = 2
    
    # 时间窗口
    NIGHT_START = "01:00"
    NIGHT_END = "06:00"
    CI_SCAN_INTERVAL = 900  # 15 分钟
    
    def should_run(self) -> bool:
        """判断是否应该运行"""
    
    def scan_backlog(self) -> List[dict]:
        """扫描待处理任务"""
    
    def run_batch(self, worker_id: str, max_jobs: int) -> BatchResult:
        """批量运行任务"""
    
    def check_fuse(self) -> bool:
        """检查保险丝状态"""
    
    def record_pr(self, pr_url: str):
        """记录 PR（更新保险丝）"""
```

### pipeline/crontab.py (新文件)
```python
def install_cron():
    """安装 cron job"""
    
def remove_cron():
    """移除 cron job"""
```

## 验收标准
- [ ] 定时触发正常工作
- [ ] 保险丝控制生效
- [ ] CI 失败扫描工作
- [ ] cron 安装/移除正常

## 验证命令
```bash
cd ~/Downloads/dispatch && python3 -c "
from pipeline.scheduler import NightShiftScheduler
s = NightShiftScheduler()
print('Should run:', s.should_run())
print('Stats:', s.get_stats())
"
```
