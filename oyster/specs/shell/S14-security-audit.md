---
task_id: S14-security-audit
project: shell-vibe-ide
priority: 1
estimated_minutes: 50
depends_on: ["S08-test-integration"]
modifies: ["web-ui/app/**/*.ts", "web-ui/app/**/*.tsx", "runner/src/index.js"]
executor: glm
---

## 目标

在 IDE 中集成安全审计面板，支持 SVM 和 EVM 合约的自动安全扫描。

## 工具

- **EVM**: Slither (静态分析) + Semgrep Solidity rules (Decurity)
- **SVM**: `cargo clippy` + 自定义 Anchor 安全 lint rules

## 步骤

1. 添加 "Audit" 按钮 (在 Deploy 按钮旁)
2. EVM 审计流程:
   - 运行 `slither . --json reports/audit.evm.slither.json`
   - 解析输出: 漏洞分类 (High/Medium/Low/Info)
   - 同时运行 `semgrep --config=p/smart-contracts --json` (如果安装了)
3. SVM 审计流程:
   - 运行 `cargo clippy -- -D warnings`
   - 解析 warning/error 输出
   - 检查常见 Anchor 安全问题 (missing signer check, missing owner check, etc.)
4. 审计结果面板:
   - 按严重程度分组 (Critical → High → Medium → Low → Info)
   - 每个发现显示: 文件名 + 行号 + 描述 + 推荐修复
   - 点击发现 → 跳转到编辑器对应行
5. 编辑器内联标注:
   - Critical/High: 红色波浪线
   - Medium: 黄色波浪线
   - Low/Info: 灰色波浪线
6. 部署前强制检查: 如果有 Critical/High 发现，Deploy 按钮标红警告
7. 报告: `reports/audit.{chain}.{tool}.json`

## UI

```
┌─ Security Audit ───────────────────┐
│ 🔴 Critical (2)                     │
│   ├ Reentrancy in withdraw()  L:45  │
│   └ Unchecked return value    L:78  │
│ 🟡 Medium (1)                       │
│   └ Missing zero-address check L:23 │
│ 🟢 Low (3)                          │
│   └ ...                             │
├─────────────────────────────────────┤
│ [Fix All with AI] [Re-scan]         │
└─────────────────────────────────────┘
```

## 验收标准

- [ ] EVM: Slither 扫描运行并生成报告
- [ ] SVM: Clippy 扫描运行并生成报告
- [ ] 审计面板按严重程度显示发现
- [ ] 点击发现跳转到代码行
- [ ] 编辑器显示内联波浪线标注
- [ ] Critical/High 时 Deploy 按钮警告
- [ ] "Fix All with AI" 按钮触发 auto-repair

## 不要做

- 不要实现付费审计服务集成
- 不要自己写安全规则 (用现有工具)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
