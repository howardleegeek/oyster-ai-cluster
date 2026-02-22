---
task_id: S05-ar-glasses-startup-opportunity-ci-cd-setup
project: ar-glasses-startup-opportunity
priority: 3
depends_on: ["S01-ar-glasses-startup-opportunity-bootstrap"]
modifies: ["backend/.github/workflows/ci-cd.yml"]
executor: glm
---
## 目标
设置CI/CD流水线，自动化测试和部署流程

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
