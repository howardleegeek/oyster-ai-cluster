---
task_id: S47-api-backend
project: shell-vibe-ide
priority: 2
estimated_minutes: 50
depends_on: ["S24-user-auth", "S25-project-management"]
modifies: ["web-ui/app/pages/api/compile.ts", "web-ui/app/pages/api/test.ts", "web-ui/app/pages/api/deploy.ts", "web-ui/app/pages/api/audit.ts", "web-ui/app/pages/api/projects.ts", "web-ui/app/lib/api/rate-limiter.ts"]
executor: glm
---

## 目标

创建 Web App 后端 API，支持编译、测试、部署等需要服务端的操作。

## 开源方案

- **Next.js API Routes**: 已有, 直接扩展
- **Supabase Edge Functions**: 无服务器函数
- **Docker**: 沙箱执行环境

## 步骤

1. API Routes:
   ```
   POST /api/compile     → 编译合约 (solc in browser 或 server)
   POST /api/test        → 运行测试 (需要 Docker 沙箱)
   POST /api/deploy      → 部署到测试网
   POST /api/audit       → 安全扫描
   GET  /api/projects    → 用户项目列表
   POST /api/projects    → 创建项目
   GET  /api/templates   → 模板列表
   POST /api/ai/chat     → AI 对话 (代理用户的 API key 或 Shell 提供)
   ```
2. 沙箱执行:
   - Docker 容器: 每个编译/测试运行在隔离容器中
   - 超时: 60 秒
   - 资源限制: 512MB RAM, 1 CPU
   - 清理: 执行后自动删除
3. AI 代理:
   - 用户自带 API key (存在客户端, 不上传)
   - Shell Pro: 提供 AI tokens (服务端代理)
4. 速率限制:
   - Free: 10 compiles/hour, 5 deploys/day
   - Pro: 100 compiles/hour, unlimited deploys

## 验收标准

- [ ] /api/compile 编译 Solidity 成功
- [ ] /api/test 运行测试 (Docker 沙箱)
- [ ] /api/deploy 部署到测试网
- [ ] 速率限制生效
- [ ] 用户鉴权 (JWT)

## 不要做

- 不要存储用户 API key
- 不要允许主网部署 (通过 API)
- 不要允许任意代码执行 (只允许合约工具链)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
