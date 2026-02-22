---
task_id: S02-ai-powered-decentralized-ai-co-ai-provider-registration
project: ai-powered-decentralized-ai-co
priority: 1
depends_on: ["S01-ai-powered-decentralized-ai-co-bootstrap"]
modifies: ["backend/providers.py", "backend/routes/providers.py"]
executor: glm
---
## 目标
实现AI提供商注册接口，允许AI提供商注册并提供其计算资源信息

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
