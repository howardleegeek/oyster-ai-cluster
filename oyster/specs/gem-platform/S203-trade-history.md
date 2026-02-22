---
task_id: S203-trade-history
project: gem-platform
priority: 2
depends_on: []
modifies: ["backend/app/routes/history.py", "backend/app/services/history.py"]
executor: glm
---
## 目标
实现交易历史 API，记录所有 NFT 买卖和 pack 开箱记录

## 约束
- 在已有 Flask app 内修改
- 写 pytest 测试
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_trade_history.py 全绿
- [ ] 支持分页查询
- [ ] 支持筛选 (buy/sell/open_pack)
- [ ] 返回交易时间、金额、NFT 详情

## 不要做
- 不留 TODO/FIXME/placeholder
