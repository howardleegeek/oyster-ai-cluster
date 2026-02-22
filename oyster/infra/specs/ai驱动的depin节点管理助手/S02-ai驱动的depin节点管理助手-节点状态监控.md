---
task_id: S02-ai驱动的depin节点管理助手-节点状态监控
project: ai驱动的depin节点管理助手
priority: 1
depends_on: ["S01-ai驱动的depin节点管理助手-bootstrap"]
modifies: ["backend/node_monitor.py"]
executor: glm
---
## 目标
实现对DePIN节点的实时状态监控，包括在线状态、运行时间等

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
