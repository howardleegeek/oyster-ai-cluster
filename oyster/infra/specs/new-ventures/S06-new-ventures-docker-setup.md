---
task_id: S06-new-ventures-docker-setup
project: new-ventures
priority: 3
depends_on: ["S01-new-ventures-bootstrap"]
modifies: ["Dockerfile", "docker-compose.yml"]
executor: glm
---
## 目标
配置Docker环境以支持项目的容器化部署

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
