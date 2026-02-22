---
task_id: S05-voice-ai-for-customer-service-database-integration
project: voice-ai-for-customer-service
priority: 2
depends_on: ["S01-voice-ai-for-customer-service-bootstrap"]
modifies: ["backend/database.py", "backend/models.py"]
executor: glm
---
## 目标
将客户交互数据存储到数据库中，以便后续分析和改进。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
