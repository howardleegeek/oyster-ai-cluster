---
task_id: S24-user-auth
project: shell-vibe-ide
priority: 2
estimated_minutes: 45
depends_on: ["S18-web-app-deploy"]
modifies: ["web-ui/app/**/*.ts", "web-ui/app/**/*.tsx", "web-ui/package.json"]
executor: glm
---

## 目标

添加用户认证系统，支持钱包登录 + GitHub OAuth。不造轮子。

## 开源方案

- **SIWE (Sign-In with Ethereum)**: github.com/spruceid/siwe — 用钱包签名登录
- **NextAuth.js**: github.com/nextauthjs/next-auth (33k stars, MIT) — OAuth 框架
- **Solana SIWS**: github.com/nickvdyck/siws — Sign-In with Solana

## 步骤

1. 安装: `pnpm add next-auth siwe @solana/wallet-adapter-react`
2. 登录方式:
   - 钱包登录 (SIWE for EVM / SIWS for Solana) — 主要
   - GitHub OAuth — 同步项目
   - Email magic link (可选)
3. 用户数据存储:
   - 使用 Supabase (bolt.diy 已有集成) 或 PlanetScale
   - 用户表: id, wallet_address, github_id, created_at
4. Session:
   - JWT token
   - 前端 context: `useAuth()` hook
5. UI:
   - 登录弹窗 (赛博朋克风格)
   - 顶栏显示用户头像/地址
   - 设置页面

## 验收标准

- [ ] MetaMask 钱包签名登录
- [ ] Phantom 钱包签名登录
- [ ] GitHub OAuth 登录
- [ ] 用户 session 持久化
- [ ] 顶栏显示登录状态

## 不要做

- 不要自己实现认证逻辑 (用 NextAuth)
- 不要存储密码
- 不要实现 email/password 注册
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
