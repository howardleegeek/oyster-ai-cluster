---
task_id: S06-ar-glasses-for-retail-and-shop-performance-optimization
project: ar-glasses-for-retail-and-shop
priority: 3
depends_on: ["S01-ar-glasses-for-retail-and-shop-bootstrap"]
modifies: ["backend/main.py", "backend/products.py"]
executor: glm
---
## 目标
优化API接口的性能，确保在高并发情况下依然能够快速响应

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
