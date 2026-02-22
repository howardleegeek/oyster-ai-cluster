---
task_id: S102-mcp-server-security
project: shell
priority: 0
estimated_minutes: 25
depends_on: []
modifies: ["mcp-server/src/server.ts"]
executor: glm
---
## 目标
修复 MCP Server 的 4 个安全 + 功能 bug (#8-#11, #36)

## Bug 清单

### Critical
8. **SSE 缺 body parser** — app.post("/messages") 没有 express.json()。修复: 加 app.use(express.json())
9. **Math.random() session ID 不安全** — 可预测。修复: 用 crypto.randomUUID() 或 crypto.randomBytes(16).toString('hex')
10. **CORS 全开** — Access-Control-Allow-Origin: *。修复: 加 CORS_ORIGIN 环境变量，默认 localhost
11. **uncaughtException 不退出** — 捕获后继续运行。修复: log 后 process.exit(1)

### High
36. **只有 ping tool** — 没有 Web3 功能。修复: 至少注册已存在的 tools/ 目录下的 tool 文件

## 验收标准
- [ ] Session ID 用 crypto 生成
- [ ] CORS 不是 * (可通过 env 配置)
- [ ] express.json() 在 POST route 前注册
- [ ] uncaughtException 后 process.exit(1)
- [ ] server 启动时注册 tools/ 目录下已有的 tool

## 不要做
- 不写新 tool 实现（S96 负责）
- 不改 MCP 协议逻辑
- 不加前端
