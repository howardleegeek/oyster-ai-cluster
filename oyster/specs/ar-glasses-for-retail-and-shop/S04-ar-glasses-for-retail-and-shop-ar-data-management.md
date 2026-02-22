---
task_id: S04-ar-glasses-for-retail-and-shop-ar-data-management
project: ar-glasses-for-retail-and-shop
priority: 2
depends_on: ["S01-ar-glasses-for-retail-and-shop-bootstrap"]
modifies: ["backend/products.py", "backend/main.py", "backend/models.py"]
executor: glm
---
## 目标
创建数据管理模块以添加、编辑和删除产品的AR展示信息

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
