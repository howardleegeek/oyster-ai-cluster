---
task_id: S10-linkedin-logging
project: linkedin-connect
priority: 10
depends_on: []
modifies:
  - backend/scripts/linkedin_cdp.py
executor: glm
---

## 目标
优化日志和错误处理，提升可观测性

## 具体改动
1. 增强 Logger 类，添加更详细的统计信息
2. 添加更详细的错误日志
3. 添加进度显示

```python
class Logger:
    def __init__(self):
        # ... existing code ...
        self.errors = []
    
    def error_detail(self, msg: str, details: dict):
        """记录详细错误"""
        error_msg = f"{msg}: {json.dumps(details)}"
        self.errors.append({"msg": msg, "details": details})
        self.log(error_msg, "ERROR")
    
    def progress(self, current: int, total: int):
        """显示进度"""
        pct = (current / total * 100) if total > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        self.log(f"Progress: [{bar}] {current}/{total} ({pct:.1f}%)")
```

## 验收标准
- [ ] 日志包含详细错误信息
- [ ] 进度条显示
