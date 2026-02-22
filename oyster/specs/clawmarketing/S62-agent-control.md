---
task_id: S62-agent-control
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - frontend/src/pages/AgentControl.tsx
---

## 目标
Agent 控制面板

## 具体改动
- 连接 /api/v2/accounts/
- 显示已连接平台账号
- 实现账号绑定 UI
