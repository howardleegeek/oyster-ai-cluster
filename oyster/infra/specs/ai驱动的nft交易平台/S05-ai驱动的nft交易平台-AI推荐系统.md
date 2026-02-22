---
task_id: S05-ai驱动的nft交易平台-AI推荐系统
project: ai驱动的nft交易平台
priority: 2
depends_on: ["S01-ai驱动的nft交易平台-bootstrap"]
modifies: ["backend/recommendation.py", "backend/main.py", "tests/test_recommendation.py"]
executor: glm
---
## 目标
开发AI驱动的推荐系统，根据用户行为和偏好推荐NFT

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
