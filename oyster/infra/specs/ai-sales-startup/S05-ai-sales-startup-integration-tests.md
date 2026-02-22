---
task_id: S05-ai-sales-startup-integration-tests
project: ai-sales-startup
priority: 2
depends_on: ["S01-ai-sales-startup-bootstrap"]
modifies: ["tests/integration_tests.py"]
executor: glm
---
## 目标
编写集成测试以验证API端点的功能，包括认证和数据操作

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
