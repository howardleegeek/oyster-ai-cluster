---
task_id: S01-019
project: clawphones
priority: 2
depends_on: []
modifies: ["proxy/tests/test_performance.py"]
executor: glm
---

## 目标
性能测试：后端负载与响应时间

## 约束
- pytest + locust
- 模拟并发请求

##具体改动
- 创建 proxy/tests/test_performance.py
  - 并发请求压力测试
  - 响应时间 p95/p99 测量
  - 速率限制验证

## 验收标准
- [ ] p95 响应时间 < 500ms
- [ ] 速率限制正确生效
- [ ] 无内存泄漏
