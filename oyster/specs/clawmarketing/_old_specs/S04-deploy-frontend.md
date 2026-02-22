---
task_id: S04-deploy-frontend
project: clawmarketing
priority: 4
depends_on: [S02-verify-startup]
modifies: []
executor: codex-node-1
---

## 目标
部署 ClawMarketing 前端到 Vercel

## 具体改动
1. 进入前端目录: cd ~/Downloads/clawmarketing/frontend
2. 确保 Vercel CLI 已安装: npm i -g vercel
3. 运行 vercel --prod 部署到生产环境
4. 验证: curl 部署后的 URL

## 验收标准
- [ ] 前端部署成功，返回 Vercel URL
- [ ] curl 部署后的 URL 可访问
