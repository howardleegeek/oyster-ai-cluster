---
task_id: S41-upgrade-ui-shadcn
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
将Frontend升级到 Next.js 15 + shadcn/ui

## 当前状态
- React 19 + Tailwind CSS 3.4
- 需要升级到生产级别UI

## 具体改动
1. 初始化 Next.js 15 项目 (如果需要)
2. 安装 shadcn/ui
3. 添加常用组件:
   - Button, Input, Card, Dialog, Dropdown
   - Form components
   - Navigation components
4. 迁移现有页面到新组件
5. 配置Vercel部署

## 约束
- 保持现有功能
- 不破坏API
- 逐步迁移

## 验收标准
- [ ] shadcn/ui 组件可用
- [ ] 页面样式升级
- [ ] Vercel部署成功
- [ ] 登录注册正常
