---
task_id: S66-foundry-script
project: shell-vibe-ide
priority: 2
estimated_minutes: 20
depends_on: ["S10-deploy", "S04-prompt-templates"]
modifies: ["web-ui/app/components/workbench/ScriptRunner.tsx", "templates/foundry-scripts/"]
executor: glm
---

## 目标

Foundry Script 集成：生成和运行 forge script 部署脚本，支持模拟和广播模式。

## 步骤

1. `templates/foundry-scripts/`:
   - `Deploy.s.sol.template` — 基础部署脚本模板
   - `Upgrade.s.sol.template` — 升级脚本模板 (配合 S50)
   - `Interaction.s.sol.template` — 交互脚本模板
2. `web-ui/app/components/workbench/ScriptRunner.tsx`:
   - 脚本生成:
     - 选择合约 → 自动填充 constructor 参数
     - 生成 `script/Deploy.s.sol`
   - 运行模式:
     - Simulate: `forge script script/Deploy.s.sol --rpc-url $RPC`
     - Broadcast: `forge script script/Deploy.s.sol --rpc-url $RPC --broadcast`
     - Verify: 添加 `--verify --etherscan-api-key $KEY`
   - 输出解析:
     - 提取部署地址
     - 提取 gas 消耗
     - 显示交易 hash
   - 运行历史记录

## 验收标准

- [ ] 生成正确的 Deploy.s.sol
- [ ] Simulate 模式可用
- [ ] Broadcast 模式可用
- [ ] 输出解析正确

## 不要做

- 不要实现 Hardhat 脚本 (只做 Foundry)
- 不要自动广播 (用户手动确认)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
