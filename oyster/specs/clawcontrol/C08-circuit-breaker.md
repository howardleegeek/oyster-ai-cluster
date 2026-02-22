---
task_id: C08-circuit-breaker
project: clawcontrol
priority: 1
depends_on: []
modifies:
  - pipeline/clawcontrol/services/breaker.py
---

## 目标
添加熔断机制，连续失败自动降级

## 具体改动
1. 失败计数
2. 自动降级模型
3. 恢复机制
