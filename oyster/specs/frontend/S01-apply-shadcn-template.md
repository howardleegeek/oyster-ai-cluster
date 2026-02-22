---
task_id: S01-frontend-template
project: frontend
priority: 1
depends_on: []
modifies:
  - ~/Downloads/frontend
executor: glm
---

## 目标
将 shadcn/ui + Next.js 模板应用到 frontend 项目

## 约束
- 不修改其他项目文件
- 使用 MIT 许可证的开源模板
- 保持目录结构清晰

## 具体改动

### 1. 选择模板
从 shadcn/ui 官方模板中选择：
- 优先使用: shadcn-ui/nextjs 或 shadcn-ui/next-app-template
- 参考: https://shadcn.io/template
- 或使用社区模板: https://github.com/topics/shadcn-ui

### 2. 应用模板到 frontend 目录
克隆选定的模板到 ~/Downloads/frontend，覆盖现有空目录结构

### 3. 保留项目元文件
保留原有的 CLAUDE.md 文件（在根目录和各子目录）

### 4. 技术栈要求
必须包含以下技术：
- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui 组件库
- 可选: TanStack Query, Zustand, etc.

### 5. 初始化 git
确保 frontend 目录有 git 仓库以便版本控制

## 验收标准
- [ ] frontend 目录包含完整的 Next.js + shadcn/ui 应用结构
- [ ] 包含 app/ 目录, components/ 目录, package.json 等核心文件
- [ ] 包含 tailwind.config.ts, next.config.js 等配置文件
- [ ] 可以运行 `npm install` 成功
- [ ] README.md 存在并说明如何启动
- [ ] 有一个可运行的示例页面

## 验证命令
```bash
ls -la ~/Downloads/frontend
ls -la ~/Downloads/frontend/app 2>/dev/null || ls -la ~/Downloads/frontend/src/app 2>/dev/null
```

## 不要做
- 不提交任何 secrets 或 .env 到 git
- 不修改 backend 项目
