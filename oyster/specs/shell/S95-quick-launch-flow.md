---
task_id: S95-quick-launch-flow
project: shell
priority: 1
estimated_minutes: 45
depends_on: [S94-build-fix-critical]
modifies: ["web-ui/app/components/chat/", "web-ui/app/lib/stores/", "web-ui/app/routes/"]
executor: glm
---
## 目标
实现 "Chat → Live Link" 闭环：用户输入 prompt → 生成合约+前端 → 一键部署 → 返回可分享 URL

## 约束
- 基于现有 bolt.diy chat 组件扩展
- 部署目标：Vercel (已有 wrangler.toml 可复用模式)
- 前端用 React + Vite 模板
- 合约用 Foundry/Hardhat 现有模板

## 实现
1. 在 chat 流里加 "Quick Launch" 按钮（生成完代码后出现）
2. QuickLaunchModal 组件：显示预览 → 确认部署 → 进度条
3. quick-launch store：管理 deploy 状态 (idle → building → deploying → live)
4. API route `/api/quick-launch`：接收生成的代码 → 打包 → 调 Vercel API 部署
5. 部署完成后显示 live URL + QR code + 分享按钮

## 验收标准
- [ ] Quick Launch 按钮在代码生成后可见
- [ ] 点击后弹出部署确认弹窗
- [ ] 部署流程有进度反馈
- [ ] 成功后显示 live URL
- [ ] URL 可复制 + 可分享

## 不要做
- 不改现有 chat 核心逻辑
- 不做真正的 Vercel API 调用（先 mock 返回一个占位 URL）
- 不动 CSS 主题
