---
task_id: FIX01-auth-provider
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - frontend/src/App.tsx
---

## 目标
修复 AuthProvider 缺失问题

## 具体改动
1. 检查 App.tsx 确保有 AuthProvider 包裹
2. 如果没有，添加 AuthProvider
3. 确保所有页面都能访问 auth context

## 验收
- [ ] Dashboard 页面正常显示
