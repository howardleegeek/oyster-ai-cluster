---
task_id: S40-fix-auth-issues
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
修复登录和注册问题

## 问题分析
1. Frontend使用localhost而非生产API
2. 注册缺少organization_slug字段
3. 登录后用户信息获取失败

## 具体改动
1. 修复 frontend/src/api/client.ts - 确保使用正确的API URL
2. 修复 frontend/src/contexts/AuthContext.tsx - 登录后获取用户信息
3. 修复 register函数 - 添加organization_slug
4. 重新部署Frontend到Vercel

## 验证
- 登录成功跳转dashboard
- 注册成功自动登录

## 不要做
- 不改后端API
- 不改其他页面
