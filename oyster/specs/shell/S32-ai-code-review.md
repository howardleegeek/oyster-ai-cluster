---
task_id: S32-ai-code-review
project: shell-vibe-ide
priority: 2
estimated_minutes: 40
depends_on: ["S14-security-audit", "S12-auto-repair-v1"]
modifies: ["web-ui/app/components/ai/code-review-panel.tsx", "web-ui/app/lib/ai/code-review.ts", "web-ui/app/lib/ai/web3-review-rules.ts"]
executor: glm
---

## 目标

添加 AI 驱动的代码审查功能，在代码编辑时提供实时建议。

## 开源方案

- **Continue** (continuedev/continue, 31.5k stars): AI 代码助手引擎
- 复用 bolt.diy 的 AI 模型连接

## 步骤

1. 实时 AI 审查:
   - 编辑器保存时触发 AI 审查
   - 检查: 安全问题, gas 优化, 最佳实践, 代码风格
   - 结果显示为编辑器内联注释
2. Web3 专属审查规则:
   - Solana: 检查 signer 验证, PDA 正确性, CPI 调用安全
   - EVM: 检查 reentrancy, overflow, access control, front-running
3. Suggestion 面板:
   - 每条建议: 位置 + 描述 + 推荐修复
   - 一键应用修复 (AI 生成 patch)
   - 忽略/标记为误报
4. 代码质量评分:
   - 安全: A-F
   - Gas 效率: A-F
   - 可读性: A-F
   - 总分

## UI

```
┌─ AI Review ────────────────────────┐
│ Score: B+ (Security: A, Gas: B)     │
│                                     │
│ 💡 L:45 Consider using unchecked   │
│   for loop counter (save ~30 gas)   │
│   [Apply Fix] [Ignore]              │
│                                     │
│ ⚠️ L:78 Missing zero-address check │
│   before transfer                   │
│   [Apply Fix] [Ignore]              │
└─────────────────────────────────────┘
```

## 验收标准

- [ ] 保存时触发 AI 审查
- [ ] 建议显示在编辑器内联
- [ ] 一键应用修复
- [ ] Web3 专属审查规则
- [ ] 代码质量评分

## 不要做

- 不要替代 Slither (这是补充)
- 不要实现实时补全 (后续做)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
