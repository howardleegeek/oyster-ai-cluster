---
task_id: S05-new-ventures-unit-tests
project: new-ventures
priority: 2
depends_on: ["S01-new-ventures-bootstrap"]
modifies: ["tests/test_main.py", "tests/test_endpoints.py", "tests/conftest.py"]
executor: glm
---
## 目标
为关键功能编写单元测试以确保代码质量

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
