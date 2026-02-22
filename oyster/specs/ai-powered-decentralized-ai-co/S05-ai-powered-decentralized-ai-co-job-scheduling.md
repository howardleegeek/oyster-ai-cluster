---
task_id: S05-ai-powered-decentralized-ai-co-job-scheduling
project: ai-powered-decentralized-ai-co
priority: 2
depends_on: ["S01-ai-powered-decentralized-ai-co-bootstrap"]
modifies: ["backend/scheduling.py", "backend/routes/scheduling.py"]
executor: glm
---
## 目标
开发作业调度模块，根据可用资源和作业需求分配计算任务给AI提供商

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
