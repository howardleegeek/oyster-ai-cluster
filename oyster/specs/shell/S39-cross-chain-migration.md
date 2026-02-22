---
task_id: S39-cross-chain-migration
project: shell-vibe-ide
priority: 3
estimated_minutes: 50
depends_on: ["S22-move-support", "S03-dual-syntax-support"]
modifies: ["web-ui/app/components/migration/migration-wizard.tsx", "web-ui/app/components/migration/migration-report.tsx", "web-ui/app/lib/migration/evm-to-svm.ts", "web-ui/app/lib/migration/svm-to-evm.ts"]
executor: glm
---

## 目标

AI 辅助的跨链合约迁移：将 EVM 合约转换为 Solana 程序（或反向）。

## 步骤

1. 迁移向导:
   - 选择源链 + 目标链
   - 上传或选择现有合约
   - AI 分析合约逻辑
   - 生成目标链代码
2. 支持的迁移路径:
   - Solidity → Rust/Anchor (EVM → SVM)
   - Rust/Anchor → Solidity (SVM → EVM)
   - Solidity → Move (EVM → Sui)
3. AI 迁移流程:
   ```
   源代码 → AI 分析:
     - 数据结构映射 (mapping → PDA, struct → Account)
     - 函数签名转换
     - 存储模型适配
     - 安全模式转换 (require → assert + error codes)
   → 生成目标代码
   → 自动构建+测试
   → 标注需要人工检查的地方
   ```
4. 迁移报告:
   - 源 vs 目标对比
   - 自动转换的部分
   - 需要手动调整的部分
   - 不可自动转换的部分 (如 EVM 特有的 msg.value)

## 验收标准

- [ ] EVM → SVM 迁移向导工作
- [ ] AI 生成目标链代码
- [ ] 自动标注需要手动调整的部分
- [ ] 迁移报告
- [ ] 生成的代码可以编译

## 不要做

- 不要保证 100% 自动转换 (标注手动部分)
- 不要实现运行时跨链 (这是代码迁移)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
