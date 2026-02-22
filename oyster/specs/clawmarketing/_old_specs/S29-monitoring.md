---
task_id: S29-monitoring
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
监控可观测性 - Health check, Prometheus metrics, 结构化日志

##具体改动
1. 创建 backend/metrics.py - Prometheus metrics
2. 增强 /health 端点 - 返回详细状态
3. 添加请求ID追踪 (middleware/request_id.py)
4. JSON格式结构化日志

##验收标准
- [ ] /health 返回数据库、Redis等状态
- [ ] Prometheus metrics可访问 (/metrics)
- [ ] 每个请求有唯一ID追踪
