---
task_id: S32-frontend-upgrade
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
升级前端到生产级别 - 使用shadcn/ui + Next.js 15

## 约束
- 使用 shadcn/ui 组件库
- 使用 Next.js 15 App Router
- 保持现有功能
- 迁移现有页面

##具体改动
1. 创建 frontend-next/ 目录
2. 使用 create-next-app 初始化 (TypeScript, Tailwind, App Router)
3. 安装 shadcn/ui
4. 迁移 pages/ 到 app/ 目录
5. 更新 API client
6. 配置 Vercel 部署

## 参考
- 后端: fastapi-large-app-template (保持现有)
- 前端: shadcn/ui + Next.js 15

##验收标准
- [ ] Next.js 15 可运行
- [ ] shadcn/ui 组件可用
- [ ] 现有页面可访问
- [ ] 可部署到 Vercel
