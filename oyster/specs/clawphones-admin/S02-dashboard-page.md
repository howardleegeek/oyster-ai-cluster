---
task_id: S02-dashboard-page
project: clawphones-admin
priority: 1
depends_on: []
modifies:
  - ~/Downloads/clawphones-admin/src/app/dashboard/
  - ~/Downloads/clawphones-admin/src/components/
executor: glm
---

## 目标
创建 Admin Portal Dashboard 页面

## 约束
- 使用 frontend 模板 (shadcn/ui + Next.js 15)
- 对接 clawphones-backend API
- 响应式设计

## 具体改动

### 1. 创建 Dashboard 页面
创建 ~/Downloads/clawphones-admin/src/app/dashboard/page.tsx:
```tsx
// 主要组件:
// - StatsCard - 统计卡片 (总用户/活跃/今日新增)
// - ActivityChart - 活动图表 (折线图)
// - RecentActivity - 最近活动列表
// - QuickActions - 快捷操作
```

### 2. 创建 Dashboard 组件
创建 ~/Downloads/clawphones-admin/src/components/dashboard/:
- StatsCard.tsx - 统计卡片
- ActivityChart.tsx - 图表 (使用 recharts)
- RecentActivity.tsx - 最近活动
- QuickActions.tsx - 快捷操作

### 3. 配置 API
```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

export const getStats = async () => {
  const res = await fetch(`${API_BASE}/admin/stats`)
  return res.json()
}
```

### 4. 添加环境变量
创建 ~/Downloads/clawphones-admin/.env.local:
```
NEXT_PUBLIC_API_URL=http://localhost:8080
```

## 验收标准
- [ ] Dashboard 页面可访问 (/dashboard)
- [ ] 统计卡片显示数据
- [ ] 图表渲染正常
- [ ] npm run build 成功

## 不要做
- 不修改 backend
