---
task_id: S913-admin-audit-log
project: gem-platform
priority: 1
depends_on: []
modifies:
  - backend/app/api/admin.py
  - backend/app/services/audit.py
executor: glm
---

## Week 1 - Admin 操作审计日志

## 目标
记录管理员操作

## 审计事件
- 改概率/改池子
- 改回购参数
- 触发 PoR 快照
- 手动改 Vault 状态

## API
GET /api/admin/audit_logs

## 验收
- [ ] 操作被记录
- [ ] 可追溯
