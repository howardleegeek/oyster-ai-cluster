---
task_id: S12-circuit-breaker
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - backend/agents/circuit_breaker.py
---

## 目标

实现 Circuit Breaker，限流自动暂停、恢复自动重启。

## 约束

- **不动 UI/CSS**

##具体改动

### CircuitBreaker

```python
class CircuitBreaker:
    """Auto-pause on rate limit, auto-resume on recovery"""
    
    STATES = ["closed", "open", "half_open"]
    
    def __init__(self):
        self.state = "closed"
        self.failure_count = 0
        self.last_failure = None
    
    async def call(self, func):
        """Execute with circuit breaker"""
        
    def record_success(self):
        """Record success"""
        
    def record_failure(self):
        """Record failure, may open circuit"""
        
    def get_state(self) -> str:
        """Get current state"""
```

### 功能

- 连续失败自动熔断
- 限流错误 (429) 触发熔断
- 自动半开尝试恢复
- 恢复后自动重启

## 验收标准

- [ ] 连续失败自动暂停
- [ ] 429 触发熔断
- [ ] 自动恢复

## 不要做

- ❌ 不改 UI
