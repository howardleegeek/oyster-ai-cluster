---
task_id: S18-web-app-deploy
project: shell-vibe-ide
priority: 2
estimated_minutes: 30
depends_on: ["S02-cyberpunk-theme", "S06-chain-selector"]
modifies: ["web-ui/package.json", "web-ui/vercel.json"]
executor: glm
---

## 目标

将 Shell Web UI 独立部署到 Vercel，作为 Web App 版本。

## 步骤

1. 确保 web-ui/ 可以独立构建:
   - `pnpm build` 成功
   - 输出到 `dist/` 或 `.next/`
2. 创建 `web-ui/vercel.json`:
   ```json
   {
     "framework": null,
     "buildCommand": "pnpm build",
     "outputDirectory": "dist"
   }
   ```
3. 处理 Tauri 依赖:
   - Web App 模式下不加载 `@tauri-apps/api`
   - 创建 `isDesktop()` 工具函数检测运行环境
   - Desktop 功能 (本地进程管理) 在 Web 模式下显示 "Desktop Only" 标签
4. Web App 限制说明:
   - 本地链 (Anvil/test-validator): 仅 Desktop
   - 本地文件系统: 仅 Desktop
   - 编译 (forge/anchor): Web 用 remix-solidity (S15) 替代
   - MCP servers: Web 通过 API proxy
5. 添加 Landing Page:
   - 简介 + 截图
   - "Try Web App" 按钮
   - "Download Desktop" 按钮
   - 赛博朋克风格
6. 部署到 Vercel (不需要询问，直接部署)

## 验收标准

- [ ] `pnpm build` 成功
- [ ] Vercel 部署成功
- [ ] Web App 不依赖 Tauri API
- [ ] Desktop-only 功能有标签提示
- [ ] Landing Page 显示
- [ ] 主要功能 (AI Chat, 代码编辑) 正常工作

## 不要做

- 不要实现用户注册/登录 (Sprint 5 做)
- 不要实现后端 API (先用纯前端)
- 不要询问是否部署，直接部署
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
