---
task_id: S05-new-venture-ai-powered-nft-va-api-endpoints
project: new-venture-ai-powered-nft-va
priority: 2
depends_on: ["S01-new-venture-ai-powered-nft-va-bootstrap"]
modifies: ["backend/main.py", "backend/endpoints.py"]
executor: glm
---
## 目标
创建用于NFT估值请求与响应的API端点

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
