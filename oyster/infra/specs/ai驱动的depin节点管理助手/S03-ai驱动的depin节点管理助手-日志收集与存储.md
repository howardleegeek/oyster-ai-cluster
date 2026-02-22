---
task_id: S03-ai驱动的depin节点管理助手-日志收集与存储
project: ai驱动的depin节点管理助手
priority: 2
depends_on: ["S01-ai驱动的depin节点管理助手-bootstrap"]
modifies: ["backend/logging_service.py", "backend/models/log.py"]
executor: glm
---
## 目标
开发日志收集模块，将节点日志实时收集并存储到数据库中

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
