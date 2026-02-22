---
task_id: S06-ar-glasses-startup-opportunity-documentation
project: ar-glasses-startup-opportunity
priority: 2
depends_on: ["S01-ar-glasses-startup-opportunity-bootstrap"]
modifies: ["backend/docs/api.md", "backend/README.md"]
executor: glm
---
## 目标
编写项目的基础文档，包括API文档和开发指南

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
