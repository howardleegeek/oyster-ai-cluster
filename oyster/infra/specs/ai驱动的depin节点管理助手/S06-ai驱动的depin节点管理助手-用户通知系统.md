---
task_id: S06-ai驱动的depin节点管理助手-用户通知系统
project: ai驱动的depin节点管理助手
priority: 3
depends_on: ["S01-ai驱动的depin节点管理助手-bootstrap"]
modifies: ["backend/notification_service.py", "backend/models/notification.py"]
executor: glm
---
## 目标
开发用户通知系统，当节点状态变化或发生故障时通知用户

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
