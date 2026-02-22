---
task_id: S202-wallet-integration
project: gem-platform
priority: 2
depends_on: []
modifies: ["backend/app/routes/wallet.py", "backend/app/services/wallet.py"]
executor: glm
---
## 目标
实现用户钱包集成，支持连接钱包、余额查询、签名验证

## 约束
- 在已有 Flask app 内修改
- 写 pytest 测试
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_wallet.py 全绿
- [ ] MetaMask 钱包连接 API
- [ ] GET /api/wallet/balance 余额查询
- [ ] 签名验证防 CSRF

## 不要做
- 不留 TODO/FIXME/placeholder
