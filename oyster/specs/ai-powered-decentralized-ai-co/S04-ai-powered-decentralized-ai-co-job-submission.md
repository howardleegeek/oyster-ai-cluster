---
task_id: S04-ai-powered-decentralized-ai-co-job-submission
project: ai-powered-decentralized-ai-co
priority: 1
depends_on: ["S01-ai-powered-decentralized-ai-co-bootstrap"]
modifies: ["backend/jobs.py", "backend/routes/jobs.py"]
executor: glm
---
## 目标
实现AI作业提交接口，允许用户提交AI作业并指定所需的计算资源

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
