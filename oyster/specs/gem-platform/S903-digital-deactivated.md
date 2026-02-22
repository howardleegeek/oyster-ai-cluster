---
task_id: S903-digital-deactivated
project: gem-platform
priority: 1
depends_on: []
modifies:
  - backend/app/api/redemption.py
  - backend/app/models/nft.py
executor: glm
---

## 目标
实现数字/实物互斥规则 - 兑换后 NFT deactivate

## 功能
1. 用户发起 Redemption
2. 批准后 NFT 状态变为 "deactivated"
3. 实物状态变为 "redeemed"
4. 避免双重兑付

## 验收
- [ ] 兑换后 NFT deactivate
- [ ] 状态互斥
