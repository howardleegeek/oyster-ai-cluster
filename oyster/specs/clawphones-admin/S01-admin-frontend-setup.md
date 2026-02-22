---
task_id: S01-admin-frontend-setup
project: clawphones-admin
priority: 1
depends_on: []
modifies:
  - ~/Downloads/clawphones-admin/src/app/dashboard/
  - ~/Downloads/clawphones-admin/src/app/tokens/
  - ~/Downloads/clawphones-admin/src/app/users/
  - ~/Downloads/clawphones-admin/src/components/dashboard/
  - ~/Downloads/clawphones-admin/src/components/tokens/
  - ~/Downloads/clawphones-admin/src/components/users/
executor: glm
---

## 目标
创建 ClawPhones Admin Portal 核心页面

## 具体改动

### 1. 创建 Dashboard 页面 (新增)
创建目录和文件:
- `src/app/dashboard/page.tsx` - Dashboard 主页面
- `src/components/dashboard/StatsCard.tsx` - 统计卡片组件
- `src/components/dashboard/ActivityChart.tsx` - 图表组件

Dashboard 页面代码示例:
```tsx
import { StatsCard } from "@/components/dashboard/StatsCard"

export default function DashboardPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard title="Total Users" value="1,234" />
        <StatsCard title="Active Now" value="567" />
        <StatsCard title="Today's New" value="89" />
        <StatsCard title="Revenue" value="$12,345" />
      </div>
    </div>
  )
}
```

### 2. 创建 Tokens 页面 (新增)
创建目录和文件:
- `src/app/tokens/page.tsx` - Token 管理页面
- `src/components/tokens/TokenTable.tsx` - Token 表格
- `src/components/tokens/TokenForm.tsx` - Token 表单

### 3. 创建 Users 页面 (新增)
创建目录和文件:
- `src/app/users/page.tsx` - 用户管理页面
- `src/components/users/UserTable.tsx` - 用户表格

### 4. 更新 layout.tsx
在 `src/app/layout.tsx` 添加导航:
```tsx
import Link from "next/link"

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/tokens", label: "Tokens" },
  { href: "/users", label: "Users" },
]
```

### 5. 创建 lib/api.ts
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"

export async function fetchStats() {
  const res = await fetch(`${API_URL}/admin/stats`)
  return res.json()
}

export async function fetchTokens() {
  const res = await fetch(`${API_URL}/admin/tokens`)
  return res.json()
}

export async function fetchUsers() {
  const res = await fetch(`${API_URL}/v1/users`)
  return res.json()
}
```

## 验收标准
- [ ] src/app/dashboard/ 目录和 page.tsx 存在
- [ ] src/app/tokens/ 目录和 page.tsx 存在
- [ ] src/app/users/ 目录和 page.tsx 存在
- [ ] src/components/dashboard/ 存在
- [ ] src/components/tokens/ 存在
- [ ] src/components/users/ 存在
- [ ] npm run build 成功

## 不要做
- 不修改 backend
