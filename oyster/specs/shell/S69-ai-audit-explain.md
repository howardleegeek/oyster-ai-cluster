---
task_id: S69-ai-audit-explain
project: shell-vibe-ide
priority: 2
estimated_minutes: 20
depends_on: ["S14-security-audit"]
modifies: ["web-ui/app/components/workbench/AuditExplainer.tsx"]
executor: glm
---

## 目标

AI 审计解读器：对 S14 安全审计结果的每个 finding 用 AI 生成通俗解释 + 修复建议 + 示例代码。

## 步骤

1. `web-ui/app/components/workbench/AuditExplainer.tsx`:
   - 读取审计报告 (S14/S17 生成的 JSON)
   - 为每个 finding 添加 "Explain" 按钮
   - 点击后调用 AI 生成:
     - 漏洞解释 (通俗语言，非安全专家也能懂)
     - 攻击场景 (1-2 句描述如何利用)
     - 修复代码 (具体的代码 diff)
     - 参考链接 (SWC Registry / Common Vulnerabilities)
   - Severity 颜色编码: Critical=红, High=橙, Medium=黄, Low=蓝
   - "Apply Fix" 按钮 → 将修复代码应用到编辑器 (复用 S12 auto-repair 的 patch 逻辑)
2. AI prompt 模板:
   - 系统: "你是智能合约安全专家..."
   - 输入: finding type + 相关代码片段
   - 输出: JSON { explanation, attackScenario, fixCode, references }

## 验收标准

- [ ] 每个 finding 有 Explain 按钮
- [ ] AI 解释通俗易懂
- [ ] 修复代码可应用
- [ ] severity 颜色正确

## 不要做

- 不要重新实现审计扫描 (用 S14 的结果)
- 不要实现批量修复 (一次修一个)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
