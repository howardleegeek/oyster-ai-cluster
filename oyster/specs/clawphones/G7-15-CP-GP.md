---
task_id: G7-15-CP-GP
project: clawphones
priority: 2
depends_on: ["G7-05-CP-CM", "G7-12-GP-CV"]
modifies: ["src/services/nft_wallet.py", "src/api/wallet.py"]
executor: glm
---
## 目标
移动端 NFT 钱包与交易功能

## 技术方案
1. 新增 `MobileNFTWallet` 服务，对接 GP 钱包 API
2. 展示用户持仓、实时价格、24h 变化
3. 快速交易：buy now / make offer
4. 推送价格提醒和营销活动

## 约束
- 复用 GP 现有交易逻辑
- 不修改 GP 核心逻辑
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] 钱包加载 < 1s
- [ ] 支持主流 NFT 交易操作
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
