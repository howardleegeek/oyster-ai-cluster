## 目标
集成 Supabase 作为后端即服务，模板自带 auth + 数据层

## 约束
- 用 @supabase/supabase-js 客户端
- 不做服务端 Supabase Admin，只做客户端集成
- 配置通过环境变量 SUPABASE_URL + SUPABASE_ANON_KEY

## 实现
1. `web-ui/app/lib/supabase/client.ts` — Supabase 客户端初始化
2. `web-ui/app/lib/supabase/auth.ts` — signUp/signIn/signOut/getUser helpers
3. `web-ui/app/lib/supabase/db.ts` — 项目 CRUD (projects table)
4. `web-ui/app/routes/api.auth.ts` — 认证 callback route
5. 在 package.json 加 `@supabase/supabase-js` 依赖
6. 模板 `templates/supabase-dapp/` — 带 auth + 数据层的 dApp 脚手架

## 验收标准
- [ ] supabase client 初始化不报错（无 key 时 graceful fallback）
- [ ] auth helpers 类型正确
- [ ] 模板目录存在且有 README
- [ ] TypeScript 编译通过

## 不要做
- 不做真实 Supabase 项目创建
- 不动现有 auth 系统
- 不改 UI 主题