---
task_id: S06-decentralized-ai-compute-marke-notification-system
project: decentralized-ai-compute-marke
priority: 2
depends_on: ["S01-decentralized-ai-compute-marke-bootstrap"]
modifies: ["backend/notifications.py", "backend/models/notification.py", "tests/test_notifications.py"]
executor: glm
---
## 目标
开发通知系统，向用户发送任务状态更新和支付确认的通知

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
