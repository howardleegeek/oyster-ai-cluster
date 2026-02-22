---
task_id: S03-ai驱动的nft交易平台-NFT创建接口
project: ai驱动的nft交易平台
priority: 1
depends_on: ["S01-ai驱动的nft交易平台-bootstrap"]
modifies: ["backend/nft.py", "backend/main.py", "tests/test_nft.py"]
executor: glm
---
## 目标
开发API接口，允许用户上传和创建NFT，包括元数据处理和存储

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
