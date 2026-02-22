---
task_id: S05-ar-glasses-for-retail-and-shop-api-testing
project: ar-glasses-for-retail-and-shop
priority: 2
depends_on: ["S01-ar-glasses-for-retail-and-shop-bootstrap"]
modifies: ["tests/test_products.py", "tests/test_auth.py"]
executor: glm
---
## 目标
编写API接口的单元测试，确保各个接口的功能正确性

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
