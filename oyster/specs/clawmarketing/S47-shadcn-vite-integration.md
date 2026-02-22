---
task_id: S47-shadcn-vite-integration
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - /Users/howardli/Downloads/clawmarketing/frontend/package.json
  - /Users/howardli/Downloads/clawmarketing/frontend/tailwind.config.js
  - /Users/howardli/Downloads/clawmarketing/frontend/src/index.css
  - /Users/howardli/Downloads/clawmarketing/frontend/src/lib/utils.ts
  - /Users/howardli/Downloads/clawmarketing/frontend/src/components/ui/button.tsx
  - /Users/howardli/Downloads/clawmarketing/frontend/src/components/ui/card.tsx
  - /Users/howardli/Downloads/clawmarketing/frontend/src/components/ui/input.tsx
  - /Users/howardli/Downloads/clawmarketing/frontend/src/components/ui/label.tsx
  - /Users/howardli/Downloads/clawmarketing/frontend/src/components/ui/textarea.tsx
  - /Users/howardli/Downloads/clawmarketing/frontend/src/components/ui/select.tsx
  - /Users/howardli/Downloads/clawmarketing/frontend/src/components/ui/dialog.tsx
  - /Users/howardli/Downloads/clawmarketing/frontend/src/components/ui/table.tsx
  - /Users/howardli/Downloads/clawmarketing/frontend/src/components/ui/badge.tsx
  - /Users/howardli/Downloads/clawmarketing/frontend/src/components/ui/avatar.tsx
  - /Users/howardli/Downloads/clawmarketing/frontend/src/components/ui/form.tsx
  - /Users/howardli/Downloads/clawmarketing/frontend/src/pages/Dashboard.tsx
  - /Users/howardli/Downloads/clawmarketing/frontend/src/pages/Login.tsx
  - /Users/howardli/Downloads/clawmarketing/frontend/src/pages/Register.tsx
  - /Users/howardli/Downloads/clawmarketing/frontend/src/pages/Accounts.tsx
  - /Users/howardli/Downloads/clawmarketing/frontend/src/components/Layout.tsx
executor: glm
---

## 目标
在 Vite + React 19 项目中集成 shadcn/ui 组件库（手动安装，不使用 Next.js CLI）

## 当前状态
- 技术栈: Vite 5 + React 19 + Tailwind CSS 3.4
- 现有组件: 只有基础 Tailwind 样式和 @headlessui/react Modal
- 项目路径: /Users/howardli/Downloads/clawmarketing/frontend/

## 约束
- 不改功能逻辑，只改 UI
- 不改 API 调用
- 保持现有测试通过
- 使用 React 19 兼容的 shadcn/ui 组件

---

## 具体改动

### Step 1: 安装必要依赖

在 `/Users/howardli/Downloads/clawmarketing/frontend/` 执行:

```bash
npm install class-variance-authority clsx tailwind-merge tailwindcss-animate @radix-ui/react-slot @radix-ui/react-label @radix-ui/react-select @radix-ui/react-dialog @radix-ui/react-table @radix-ui/react-avatar @radix-ui/react-checkbox @radix-ui/react-scroll-area
```

验证:
```bash
npm list class-variance-authority clsx tailwind-merge tailwindcss-animate
```

### Step 2: 配置 Tailwind

修改 `tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

验证:
```bash
cd /Users/howardli/Downloads/clawmarketing/frontend && npx tailwindcss --version
```

### Step 3: 添加 CSS 变量

修改 `src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 53.3%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 224.3 76.3% 48%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

验证:
```bash
head -30 /Users/howardli/Downloads/clawmarketing/frontend/src/index.css
```

### Step 4: 创建 lib/utils.ts

创建文件 `src/lib/utils.ts`:
```typescript
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

验证:
```bash
ls -la /Users/howardli/Downloads/clawmarketing/frontend/src/lib/utils.ts
```

### Step 5: 创建 UI 组件

按以下结构创建组件 (从 shadcn/ui 官方复制源码，只改 import 路径):

**目录结构:**
```
src/components/ui/
  button.tsx
  card.tsx
  input.tsx
  label.tsx
  textarea.tsx
  select.tsx
  dialog.tsx
  table.tsx
  badge.tsx
  avatar.tsx
  form.tsx
```

**button.tsx** - 使用 cn() 合并 className
**card.tsx** - Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter
**input.tsx** - 带 ring 和 border 样式
**label.tsx** - 使用 @radix-ui/react-label
**textarea.tsx** - 类似 input
**select.tsx** - 使用 @radix-ui/react-select
**dialog.tsx** - 使用 @radix-ui/react-dialog + Transition
**table.tsx** - Table, TableHeader, TableBody, TableRow, TableHead, TableCell
**badge.tsx** - 变体: default, secondary, destructive, outline
**avatar.tsx** - 使用 @radix-ui/react-avatar
**form.tsx** - 使用 react-hook-form + zod (可选，先做简单版)

验证:
```bash
ls /Users/howardli/Downloads/clawmarketing/frontend/src/components/ui/
```

### Step 6: 迁移页面

**1. Login.tsx** - 使用 Card, Input, Button
**2. Register.tsx** - 使用 Card, Input, Button  
**3. Dashboard.tsx** - 使用 Card, Button
**4. Accounts.tsx** - 使用 Table, Button, Input, Dialog
**5. Layout.tsx** - 保持导航，改按钮样式

验证:
```bash
cd /Users/howardli/Downloads/clawmarketing/frontend && npm run build
```

### Step 7: 运行测试

```bash
cd /Users/howardli/Downloads/clawmarketing/frontend && npm test -- --run
```

---

## 验收标准

### 1. 依赖安装
- [ ] `npm list` 显示 class-variance-authority, clsx, tailwind-merge, tailwindcss-animate
- [ ] 无 install 错误

### 2. 配置验证
- [ ] tailwind.config.js 包含 colors, borderRadius 配置
- [ ] index.css 包含 CSS 变量定义
- [ ] lib/utils.ts 存在且导出 cn() 函数

### 3. 组件验证
- [ ] src/components/ui/ 目录下有 12 个组件文件
- [ ] 每个组件可以 import 使用

### 4. 页面迁移
- [ ] Login.tsx 使用 shadcn/ui Card, Input, Button
- [ ] Register.tsx 使用 shadcn/ui Card, Input, Button
- [ ] Dashboard.tsx 使用 shadcn/ui Card
- [ ] Accounts.tsx 使用 shadcn/ui Table, Button

### 5. 构建验证
- [ ] `npm run build` 成功，无 error
- [ ] `npm test -- --run` 全部测试通过

### 6. 功能验证 (可选 - 需要启动 dev server)
- [ ] 登录页面显示 shadcn/ui 风格
- [ ] 注册页面显示 shadcn/ui 风格
- [ ] Dashboard 显示 Card 组件样式

---

## 不要做
- 不改变任何 API 调用
- 不改变任何功能逻辑
- 不删除现有组件 (只替换 UI)
- 不添加新的路由
- 不修改 vite.config.ts (除非需要)
- 不使用 Next.js 相关的包

---

## 关键路径参考
- 项目: /Users/howardli/Downloads/clawmarketing/frontend/
- 组件源码: https://ui.shadcn.com/docs/components/button (复制源码，去掉 "use client")
- CSS 变量: https://ui.shadcn.com/docs/theming
