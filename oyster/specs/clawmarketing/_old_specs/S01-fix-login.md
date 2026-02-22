---
task_id: S01-fix-login
project: clawmarketing
priority: 1
depends_on: []
modifies: ["frontend/src/contexts/AuthContext.tsx"]
executor: local
---

## 目标
修复前端登录问题

## 具体改动
1. 修改 AuthContext.tsx 中 login 函数
2. 将 `{ email, password }` 改为 `{ username: email, password }`
3. 重新部署前端到 Vercel

## 验收标准
- [ ] 用户可以使用 email 登录
