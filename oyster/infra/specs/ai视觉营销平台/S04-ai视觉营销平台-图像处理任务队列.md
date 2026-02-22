---
task_id: S04-ai视觉营销平台-图像处理任务队列
project: ai视觉营销平台
priority: 2
depends_on: ["S01-ai视觉营销平台-bootstrap"]
modifies: ["backend/tasks.py", "backend/worker.py"]
executor: glm
---
## 目标
集成任务队列系统（如Celery）以处理AI图像分析任务

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
