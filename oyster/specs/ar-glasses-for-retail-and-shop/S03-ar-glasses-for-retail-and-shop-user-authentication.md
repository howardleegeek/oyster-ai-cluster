---
task_id: S03-ar-glasses-for-retail-and-shop-user-authentication
project: ar-glasses-for-retail-and-shop
priority: 1
depends_on: ["S01-ar-glasses-for-retail-and-shop-bootstrap"]
modifies: ["backend/auth.py", "backend/main.py"]
executor: glm
---
## 目标
实现用户认证和授权机制，确保只有授权用户可以访问AR数据

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
