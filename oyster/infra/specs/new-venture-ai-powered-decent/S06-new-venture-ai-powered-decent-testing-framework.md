---
task_id: S06-new-venture-ai-powered-decent-testing-framework
project: new-venture-ai-powered-decent
priority: 3
depends_on: ["S01-new-venture-ai-powered-decent-bootstrap"]
modifies: ["tests/test_main.py", "tests/conftest.py"]
executor: glm
---
## 目标
设置测试框架，编写基础测试用例以确保主要功能的正确性。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
