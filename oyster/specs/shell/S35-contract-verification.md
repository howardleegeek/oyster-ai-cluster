---
task_id: S35-contract-verification
project: shell-vibe-ide
priority: 2
estimated_minutes: 35
depends_on: ["S10-deploy"]
modifies: ["web-ui/app/**/*.ts", "runner/src/index.js"]
executor: glm
---

## 目标

部署后一键验证合约源码到区块浏览器 (Etherscan/Solscan)。

## 开源方案

- **forge verify-contract**: Foundry 内置验证
- **Sourcify**: github.com/ethereum/sourcify — 开源合约验证服务
- **Solscan API**: Solana 合约验证

## 步骤

### EVM
1. 部署成功后显示 "Verify" 按钮
2. 调用 `forge verify-contract`:
   ```bash
   forge verify-contract {address} {ContractName} \
     --chain {chain-id} \
     --etherscan-api-key {key}
   ```
3. 或使用 Sourcify (无需 API key):
   ```bash
   forge verify-contract {address} {ContractName} \
     --verifier sourcify
   ```
4. 验证成功后:
   - 显示绿色 "Verified ✓"
   - 链接到 Etherscan 已验证页面

### SVM
1. Anchor 程序自动生成 IDL
2. 上传 IDL 到 Anchor Program Registry
3. 可选: 提交到 Solscan verified programs

## 验收标准

- [ ] EVM: forge verify-contract 集成
- [ ] Sourcify 验证工作
- [ ] Etherscan 验证工作 (需要 API key)
- [ ] 验证状态显示
- [ ] SVM: IDL 上传

## 不要做

- 不要自己实现验证逻辑 (用 forge/sourcify)
- 不要存储 API key (用户输入/环境变量)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
