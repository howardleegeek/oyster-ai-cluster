---
task_id: S02-ar-glasses-for-retail-and-shop-product-data-api
project: ar-glasses-for-retail-and-shop
priority: 1
depends_on: ["S01-ar-glasses-for-retail-and-shop-bootstrap"]
modifies: ["backend/products.py", "backend/main.py"]
executor: glm
---
## 目标
开发API接口以获取零售和购物产品的AR展示数据

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
