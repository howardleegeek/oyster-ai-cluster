---
task_id: S08-linkedin-rate-limit
project: linkedin-connect
priority: 8
depends_on: []
modifies:
  - backend/scripts/linkedin_cdp.py
executor: glm
---

## 目标
增强 Rate Limit 检测和自动处理

## 具体改动
改进 `check_rate_limit` 方法：

```python
def check_rate_limit(self) -> bool:
    """检测是否被限流"""
    try:
        page_text = self.page.content().lower()
        
        rate_limit_indicators = [
            "you've reached a limit",
            "rate limit",
            "too many requests",
            "please try again later",
            "限制",
            "操作过于频繁",
            "connection limit",
            "too many attempts",
        ]
        
        detected = [ind for ind in rate_limit_indicators if ind in page_text]
        
        if detected:
            self.logger.log(f"Rate limit detected: {detected}")
            return True
            
        return False
    except:
        return False
```

并在 `process_single_person` 中添加 rate limit 处理：

```python
if self.check_rate_limit():
    self.logger.log("Rate limited! Waiting 60 seconds...")
    time.sleep(60)
    return False
```

## 验收标准
- [ ] 能检测 rate limit
- [ ] 自动等待恢复
