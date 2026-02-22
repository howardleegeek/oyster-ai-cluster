---
task_id: S12-auto-repair-v1
project: shell-vibe-ide
priority: 1
estimated_minutes: 60
depends_on: ["S05-build-integration", "S08-test-integration"]
modifies: ["web-ui/app/**/*.ts", "web-ui/app/**/*.tsx"]
executor: glm
---

## 目标

实现 AI 自动修复闭环 v1：构建/测试失败 → AI 读取错误报告 → 生成修复 patch → 重新构建/测试 → 直到通过。

## 工作流

```
用户点击 Build/Test
  ↓
执行命令 → 生成报告
  ↓
报告 ok=false?
  ├── 是 → 读取报告错误信息
  │        ↓
  │   构建 AI prompt:
  │   "以下是构建/测试错误: {errors}
  │    当前代码: {code}
  │    请修复这些错误，只输出修改后的代码"
  │        ↓
  │   AI 生成修复代码
  │        ↓
  │   替换文件内容
  │        ↓
  │   重新 Build/Test (最多 3 轮)
  │        ↓
  │   仍然失败? → 停止，显示给用户手动修复
  │
  └── 否 → 显示成功，继续下一步
```

## 实现

1. 在 Build/Test 完成后检查报告的 `ok` 字段
2. 如果 `ok === false`:
   a. 读取 `details.errors` 中的错误信息
   b. 读取当前打开的源文件内容
   c. 构建修复 prompt 发给 AI
   d. AI 返回修复后的代码
   e. 替换编辑器中的代码
   f. 自动触发重新 Build/Test
3. 最多重试 3 轮
4. UI 显示修复状态:
   - "Auto-repairing... (attempt 1/3)"
   - 进度指示器 (绿色旋转环)
   - 每轮修复的 diff 预览
5. 3 轮后仍失败 → 停止，显示最后的错误给用户

## UI

```
┌─ Auto-Repair ──────────────────────┐
│ ⟳ Fixing build errors (1/3)        │
│                                     │
│ Error: AccountNotInitialized        │
│ Fix: Adding init constraint to      │
│      account struct...              │
│                                     │
│ [Cancel] [Skip to manual fix]       │
└─────────────────────────────────────┘
```

## 验收标准

- [ ] Build 失败后自动触发修复流程
- [ ] AI 读取错误信息并生成修复代码
- [ ] 修复后自动重新 Build
- [ ] 最多重试 3 轮
- [ ] 3 轮失败后停止并通知用户
- [ ] UI 显示修复进度
- [ ] 可手动取消修复

## 不要做

- 不要在测试中也触发 (先只做 build 修复)
- 不要实现 OpenCrabs 集成 (S20 做)
- 不要改 AI 模型配置
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
