## 目标

将 Shell MCP Server 接入前端 MCP 客户端，使 AI 能在聊天中调用 Web3 工具。

## 背景

Shell 前端已有 MCP 客户端基础设施 (mcpService.ts)，支持 SSE transport。只需要添加默认的 Shell MCP Server 配置，让 AI 自动发现 forge_test 等工具。

## 步骤

1. 修改 `web-ui/app/lib/services/mcpService.ts`:
   - 添加默认 MCP Server 配置:
     ```typescript
     const DEFAULT_SHELL_MCP: MCPServerConfig = {
       name: 'shell-web3-tools',
       type: 'sse',
       url: process.env.SHELL_MCP_URL || 'http://localhost:3001/sse',
       autoConnect: true,
       description: 'Shell Web3 development tools (Forge, Anvil, etc.)'
     };
     ```
   - 在 MCP 服务初始化时自动连接 Shell MCP Server
   - 如果连接失败，不阻塞 (降级为无工具模式)

2. 修改 `web-ui/app/routes/api.mcp-check.ts`:
   - 添加对 Shell MCP Server 的健康检查
   - 返回 `{ shellMcp: { online: boolean, tools: string[] } }`

3. 在设置页面添加 MCP Server URL 配置:
   - 在 ProvidersTab 或新建 ToolsTab 中添加
   - 输入框: "Shell MCP Server URL"
   - 默认值: `http://localhost:3001/sse`
   - 连接状态指示 (绿/红)

4. 添加环境变量 `SHELL_MCP_URL` 到 `.env.example`

## 约束

- MCP 连接失败不能阻塞聊天功能
- 保持与现有 MCP 配置的兼容性 (用户自定义的 MCP servers 不受影响)
- 不要硬编码 URL，必须可配置

## 验收标准

- [ ] 启动 web-ui 时自动连接 Shell MCP Server (如果在跑)
- [ ] AI 聊天中可以调用 forge_test 等工具
- [ ] MCP Server 离线时 web-ui 正常工作 (降级模式)
- [ ] 设置页面可以修改 MCP Server URL
- [ ] npm test 全部通过 (不能破坏现有测试)

## 不要做

- 不要删除现有 MCP 配置能力
- 不要把 MCP URL 硬编码
- 不要修改 mcp-server/ 的代码