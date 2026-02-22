---
task_id: S04-ar-glasses-startup-opportunity-unit-tests
project: ar-glasses-startup-opportunity
priority: 2
depends_on: ["S01-ar-glasses-startup-opportunity-bootstrap"]
modifies: ["tests/test_user.py", "tests/test_device.py"]
executor: glm
---
## 目标
为API端点编写单元测试，确保基本功能正确

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
