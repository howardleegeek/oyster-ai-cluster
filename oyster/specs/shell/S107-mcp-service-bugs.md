---
task_id: S107-mcp-service-bugs
project: shell
priority: 0
estimated_minutes: 30
depends_on: []
modifies: ["web-ui/app/lib/services/mcpService.ts"]
executor: glm
---
## 目标
修复 MCP Service 层 8 个 bug (#17-#24)

## Bug 清单

17. Zod 错误上下文丢失 — 保留完整 error stack，不只 join messages
18. `_createClients` 旧实例未释放 — 在创建新 client 前 close 旧的 handles
19. 连接断开无重连 — SSE/HTTP 加 reconnection 逻辑 (exponential backoff, max 5 retries)
20. `updateConfig` 无 deep-equal — 加 JSON.stringify 对比，相同则跳过 restart
21. `client.tools()` 无超时 — 包装 Promise.race + 30s timeout
22. `messages[messages.length - 1]` 脏数据 — 从后往前查找最近的 tool message type
23. `toolInstance.execute()` 无 timeout — Promise.race 限制 60s
24. 强制赋值 readonly 对象 — `config.type = 'stdio'` 改为 `{ ...config, type: config.type || 'stdio' }`

## 验收标准
- [ ] 旧 client 在 recreate 前被 close
- [ ] updateConfig 相同配置不重启
- [ ] tools() 和 execute() 都有超时
- [ ] readonly 对象不被直接修改
- [ ] TypeScript 编译通过

## 不要做
- 不改 MCP 协议实现
- 不加新 tool
- 不动 UI
