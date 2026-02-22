---
task_id: S36-prometheus-metrics
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
添加Prometheus metrics监控

##具体改动
1. 创建 backend/metrics.py - Prometheus指标
2. 添加 /metrics 端点
3. 记录请求计数、延迟、错误率等

##验收标准
- [ ] /metrics 端点可访问
- [ ] 有请求计数指标
- [ ] 有延迟指标
