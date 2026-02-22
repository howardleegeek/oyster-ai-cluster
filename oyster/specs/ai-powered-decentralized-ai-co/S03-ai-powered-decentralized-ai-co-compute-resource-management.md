---
task_id: S03-ai-powered-decentralized-ai-co-compute-resource-management
project: ai-powered-decentralized-ai-co
priority: 1
depends_on: ["S01-ai-powered-decentralized-ai-co-bootstrap"]
modifies: ["backend/resources.py", "backend/routes/resources.py"]
executor: glm
---
## 目标
开发计算资源管理模块，处理AI提供商注册的计算资源，包括添加、更新和删除资源

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
