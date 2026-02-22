---
task_id: S89-deploy-web-ui
project: shell
priority: 1
estimated_minutes: 30
depends_on: []
modifies: ["web-ui/wrangler.toml", "web-ui/.env.example", ".github/workflows/deploy.yml"]
executor: glm
---

## 目标

将 Shell web-ui 部署到 Cloudflare Pages，让用户可以通过公开 URL 试用。

## 步骤

1. 更新 `web-ui/wrangler.toml`:
   - 将 `name` 从 "bolt" 改为 "shell-web3"
   - 确认 `pages_build_output_dir` 指向正确的构建产物目录

2. 创建 `.github/workflows/deploy.yml`:
   ```yaml
   name: Deploy to Cloudflare Pages
   on:
     push:
       branches: [main]
       paths: ['web-ui/**']
     workflow_dispatch:
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-node@v4
           with:
             node-version: '20'
         - name: Install pnpm
           run: npm install -g pnpm
         - name: Install dependencies
           run: cd web-ui && pnpm install --frozen-lockfile
         - name: Build
           run: cd web-ui && pnpm build
         - name: Deploy to Cloudflare Pages
           uses: cloudflare/wrangler-action@v3
           with:
             apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
             accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
             command: pages deploy web-ui/build/client --project-name=shell-web3
   ```

3. 更新 `web-ui/.env.example` 添加必需的环境变量说明

4. 确保 `web-ui/build.js` 能成功构建完整的 SSR + client 产物

## 约束

- 使用 Cloudflare Pages (已有 wrangler.toml)
- 不要修改 web-ui 核心代码
- 构建必须在 CI 环境下通过 (无本地依赖)

## 验收标准

- [ ] `pnpm build` 在 web-ui 目录下成功
- [ ] GitHub Actions workflow 文件语法正确
- [ ] wrangler.toml 项目名更新为 shell-web3
- [ ] .env.example 包含所有必需变量

## 不要做

- 不要修改 web-ui 的组件代码
- 不要添加新依赖
- 不要配置自定义域名 (后续再做)
