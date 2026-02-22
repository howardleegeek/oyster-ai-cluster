---
task_id: S03-decentralized-ai-compute-marke-resource-management
project: decentralized-ai-compute-marke
priority: 1
depends_on: ["S01-decentralized-ai-compute-marke-bootstrap"]
modifies: ["backend/resources.py", "backend/models/resource.py", "tests/test_resources.py"]
executor: glm
---
## 目标
开发资源管理模块，允许用户添加、删除和列出可用的AI计算资源

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
