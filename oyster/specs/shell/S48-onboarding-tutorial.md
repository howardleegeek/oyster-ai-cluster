---
task_id: S48-onboarding-tutorial
project: shell-vibe-ide
priority: 3
estimated_minutes: 35
depends_on: ["S04-prompt-templates", "S16-template-gallery"]
modifies: ["web-ui/app/components/onboarding/tutorial.tsx", "web-ui/app/components/onboarding/tutorial-steps.ts", "web-ui/app/lib/onboarding/tutorial-state.ts"]
executor: glm
---

## 目标

创建交互式新手引导教程，帮助用户快速上手。

## 开源方案

- **react-joyride**: github.com/gilbarbara/react-joyride (7k stars, MIT) — 步骤式引导
- **driver.js**: github.com/nickvdyck/driver.js (20k stars, MIT) — 轻量级引导
- **intro.js**: github.com/usablica/intro.js (23k stars, AGPL)

## 步骤

1. 安装: `pnpm add driver.js` (最轻量, MIT)
2. 引导步骤 (10 步):
   1. 欢迎 — "Welcome to Shell, the Web3 Vibe Coding IDE"
   2. 链选择器 — "Choose your chain: SVM or EVM"
   3. 模板画廊 — "Pick a template to get started"
   4. AI Chat — "Describe what you want, AI will generate it"
   5. 代码编辑器 — "Review and edit the generated code"
   6. Build — "Build your contract with one click"
   7. Test — "Run tests automatically"
   8. Audit — "Security scan before deploy"
   9. Deploy — "Deploy to testnet"
   10. Done — "You're ready! Start building Web3"
3. 触发条件:
   - 首次使用 (localStorage 标记)
   - 可以在设置中重新触发
4. 交互式 demo:
   - 引导中实际执行一个 "Hello World" 合约
   - 用户跟着步骤操作
5. 赛博朋克风格:
   - 高亮区域用 neon 绿边框
   - 提示框暗底 + 绿色文字

## 验收标准

- [ ] 首次打开显示引导
- [ ] 10 步引导完整走完
- [ ] 可以跳过引导
- [ ] 可以在设置中重新触发
- [ ] 赛博朋克风格

## 不要做

- 不要用 intro.js (AGPL)
- 不要做视频教程 (先做交互式)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
