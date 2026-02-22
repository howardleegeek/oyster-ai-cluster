---
task_id: S20-auto-repair-v2
project: shell-vibe-ide
priority: 1
estimated_minutes: 60
depends_on: ["S12-auto-repair-v1", "S14-security-audit"]
modifies: ["web-ui/app/lib/auto-repair.ts", "web-ui/app/components/auto-repair/repair-state-machine.ts", "web-ui/app/components/auto-repair/repair-progress.tsx"]
executor: glm
---

## 目标

Auto-repair v2: 扩展到测试修复 + 安全漏洞修复，集成 OpenCrabs 状态机。

## 与 v1 的区别

- v1: 只修复 build errors
- v2: 修复 build + test + audit findings

## 工作流

```
1. Build → 失败 → AI 修复 → 重 build (v1 已有)
2. Test → 失败 → AI 读取失败测试报告 → 分析原因 → patch 代码 → 重 test (新)
3. Audit → Critical/High → AI 读取审计报告 → 生成安全 patch → 重审计 (新)
4. 全流程闭环: Build ✓ → Test ✓ → Audit ✓ → Ready to Deploy
```

## 步骤

1. 扩展 auto-repair 到测试失败:
   - 读取 `reports/test.*.json` 的失败测试
   - 构建 prompt: 测试名 + 错误信息 + 相关代码
   - AI 生成修复 → 替换 → 重新测试
2. 扩展到审计发现:
   - 读取 `reports/audit.*.json` 的 Critical/High 发现
   - 构建 prompt: 漏洞类型 + 位置 + 推荐修复
   - AI 生成安全 patch → 替换 → 重新审计
3. 全流程状态机:
   ```
   IDLE → BUILDING → BUILD_OK → TESTING → TEST_OK → AUDITING → AUDIT_OK → READY
                  ↗                    ↗                    ↗
         BUILD_FAIL → REPAIRING   TEST_FAIL → REPAIRING   AUDIT_FAIL → REPAIRING
   ```
4. UI 状态指示器:
   - 进度条显示当前阶段
   - 每个阶段的通过/失败状态
   - 修复尝试计数

## 验收标准

- [ ] 测试失败触发 auto-repair
- [ ] 审计 Critical/High 触发 auto-repair
- [ ] 全流程状态机正常运转
- [ ] Build ✓ → Test ✓ → Audit ✓ 到 Ready
- [ ] UI 显示完整流程进度
- [ ] 每阶段最多重试 3 轮

## 不要做

- 不要修复 Low/Info 级别审计发现
- 不要实现 OpenCrabs Rust 调用 (这里用 JS/TS)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
