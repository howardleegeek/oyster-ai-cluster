---
task_id: S65-ens-resolution
project: shell-vibe-ide
priority: 3
estimated_minutes: 15
depends_on: ["S11-wallet-connection"]
modifies: ["web-ui/app/components/workbench/EnsResolver.tsx"]
executor: glm
---

## 目标

ENS/SNS 名称解析：在 IDE 中支持 .eth 和 .sol 域名解析，显示地址 ↔ 名称映射。

## 步骤

1. `web-ui/app/components/workbench/EnsResolver.tsx`:
   - 输入框: 粘贴地址或域名
   - EVM (.eth):
     - 正向: name → address (ethers.provider.resolveName)
     - 反向: address → name (ethers.provider.lookupAddress)
     - 显示 avatar, text records
   - SVM (.sol):
     - 用 @bonfida/spl-name-service 解析
     - 正向/反向解析
   - 复制按钮
   - 在合约交互 (S21) 的地址输入框中也支持 ENS/SNS

## 验收标准

- [ ] .eth 正向/反向解析
- [ ] .sol 正向/反向解析
- [ ] 地址复制功能

## 不要做

- 不要实现 ENS 注册
- 不要缓存解析结果到服务端
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
