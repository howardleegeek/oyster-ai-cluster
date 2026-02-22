---
task_id: S100-vercel-deploy-integration
project: shell
priority: 1
estimated_minutes: 35
depends_on: [S95-quick-launch-flow]
modifies: ["web-ui/app/lib/deploy/", "web-ui/app/routes/api.deploy.ts"]
executor: glm
---
## 目标
实现真正的 Vercel 部署集成，替换 Quick Launch 里的 mock

## 约束
- 用 Vercel REST API (不用 CLI)
- API token 通过环境变量 VERCEL_TOKEN
- 部署生成的 React 前端项目

## 实现
1. `web-ui/app/lib/deploy/vercel.ts` — Vercel API 客户端 (createDeployment, getDeployment, listDeployments)
2. `web-ui/app/lib/deploy/packager.ts` — 把生成的代码打包成 Vercel 部署格式
3. `web-ui/app/routes/api.deploy.ts` — 部署 API route (接收代码 → 打包 → 调 Vercel → 返回 URL)
4. `web-ui/app/lib/deploy/ipfs.ts` — IPFS 部署备选 (用 web3.storage 或 pinata)
5. 部署状态轮询 + webhook

## 验收标准
- [ ] Vercel 部署客户端类型正确
- [ ] 打包器能生成 Vercel files 格式
- [ ] API route 有错误处理 (无 token 时返回说明)
- [ ] IPFS 部署函数存在
- [ ] TypeScript 编译通过

## 不要做
- 不做 AWS/GCP 部署
- 不改前端 UI (由 S95 负责)
- 不存用户密钥
