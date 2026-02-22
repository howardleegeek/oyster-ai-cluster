---
task_id: S04-decentralized-ai-compute-marke-job-submission
project: decentralized-ai-compute-marke
priority: 1
depends_on: ["S01-decentralized-ai-compute-marke-bootstrap"]
modifies: ["backend/jobs.py", "backend/models/job.py", "tests/test_jobs.py"]
executor: glm
---
## 目标
实现AI计算任务的提交功能，包括任务参数设置和任务状态跟踪

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
