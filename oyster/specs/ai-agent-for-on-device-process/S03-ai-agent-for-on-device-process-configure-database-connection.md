---
task_id: S03-ai-agent-for-on-device-process-configure-database-connection
project: ai-agent-for-on-device-process
priority: 1
depends_on: ["S01-ai-agent-for-on-device-process-bootstrap"]
modifies: ["backend/database.py", "backend/models.py"]
executor: glm
---
## 目标
配置数据库连接并创建基础数据模型

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
