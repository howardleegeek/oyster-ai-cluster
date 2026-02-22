---
task_id: S71-mcp-server-scaffold
project: shell
priority: 1
estimated_minutes: 30
depends_on: []
modifies: ["mcp-server/package.json", "mcp-server/tsconfig.json", "mcp-server/src/server.ts", "mcp-server/src/types.ts"]
executor: glm
---

## 目标

创建 Shell MCP Server 项目骨架，使用 @modelcontextprotocol/sdk 实现一个 MCP 工具服务器。

## 背景

Shell Web3 IDE 前端已有 MCP 客户端 (app/lib/services/mcpService.ts)，支持 stdio/sse/streamable-http 三种传输方式。我们需要一个后端 MCP Server 提供 Web3 工具 (forge test, deploy 等)。

## 步骤

1. 在项目根目录创建 `mcp-server/` 目录
2. 创建 `mcp-server/package.json`:
   - name: `"shell-mcp-server"`
   - dependencies: `@modelcontextprotocol/sdk`, `zod`
   - devDependencies: `typescript`, `tsx`, `@types/node`
   - scripts: `"start": "tsx src/server.ts"`, `"build": "tsc"`, `"dev": "tsx watch src/server.ts"`
3. 创建 `mcp-server/tsconfig.json`: target ES2022, module NodeNext, strict true
4. 创建 `mcp-server/src/server.ts`:
   - 使用 `@modelcontextprotocol/sdk/server` 的 `McpServer`
   - 使用 `StdioServerTransport` (默认) 和 `SSEServerTransport` (HTTP模式)
   - 注册一个 `ping` 工具用于健康检查
   - 命令行参数: `--transport stdio|sse --port 3001`
5. 创建 `mcp-server/src/types.ts`:
   - `ForgeTestResult` 接口 (test_name, status, gas_used, logs)
   - `BuildResult` 接口 (success, abi, bytecode, errors)
   - `DeployResult` 接口 (address, tx_hash, chain)
   - `ReportData` 接口 (timestamp, results[], summary)

## 约束

- 使用 TypeScript strict mode
- 不依赖 web-ui 的任何代码
- MCP Server 是独立进程
- 不要安装 Foundry/Forge (其他 spec 会做)

## 验收标准

- [ ] `cd mcp-server && npm install` 成功
- [ ] `cd mcp-server && npm start -- --transport stdio` 启动不报错
- [ ] ping 工具可通过 MCP 协议调用返回 "pong"
- [ ] TypeScript 编译无错误

## 不要做

- 不要修改 web-ui/ 下的任何文件
- 不要实现具体的 forge/anchor 工具 (其他 spec 负责)
- 不要添加 Docker 配置 (S78 负责)
