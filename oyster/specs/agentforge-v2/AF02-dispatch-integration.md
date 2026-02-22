---
task_id: AF02-dispatch-integration
project: agentforge-v2
priority: 1
estimated_minutes: 45
depends_on: []
modifies: ["packages/server/src/services/", "packages/server/src/routes/"]
executor: glm
---
## 目标
在 AgentForge server 中添加 Oyster Dispatch 集成层，让 workflow 执行可以分发到 dispatch 集群

## 技术方案
1. 在 `packages/server/src/services/` 创建 `dispatch-bridge.ts`：
   - 连接 dispatch controller API (HTTP)
   - 将 Flowise chatflow execution 转换为 dispatch task
   - 接收 task 完成回调
2. 在 `packages/server/src/routes/` 添加 `/api/v1/dispatch/` 路由：
   - POST /api/v1/dispatch/submit — 提交 workflow 到 dispatch
   - GET /api/v1/dispatch/status/:taskId — 查询任务状态
   - GET /api/v1/dispatch/nodes — 查看可用节点
3. 配置 .env 添加 DISPATCH_CONTROLLER_URL

## 约束
- TypeScript, 用现有的 express router 模式
- 不改 Flowise 核心 chatflow 执行逻辑
- dispatch bridge 作为可选功能（DISPATCH_ENABLED=true 启用）
- 不新建超过 3 个文件

## 验收标准
- [ ] dispatch-bridge.ts 可以发送 HTTP 请求到 controller
- [ ] /api/v1/dispatch/submit 接受 chatflowId + input 参数
- [ ] /api/v1/dispatch/status 返回任务状态
- [ ] DISPATCH_ENABLED=false 时所有功能跳过
- [ ] npm run build 通过

## 不要做
- 不改 Flowise 核心执行引擎
- 不加新的 npm 依赖（用内置 fetch/http）
- 不改 UI
