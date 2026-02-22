---
task_id: S06-ai-powered-nft-valuation-api-endpoints
project: ai-powered-nft-valuation
priority: 1
depends_on: ["S01-ai-powered-nft-valuation-bootstrap"]
modifies: ["backend/main.py", "backend/endpoints.py"]
executor: glm
---
## 目标
创建FastAPI端点，允许用户提交NFT估值请求并获取结果

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
