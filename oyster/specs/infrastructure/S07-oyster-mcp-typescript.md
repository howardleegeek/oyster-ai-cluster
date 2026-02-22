---
task_id: S07-oyster-mcp-typescript
project: infrastructure
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
创建 oyster-mcp TypeScript 包 - 支持 MCP Client + Agent + Server + Inspector

## 约束
- 不改现有前端项目
- 基于 mcp-use TypeScript 改写
- 保持 MIT 协议

## 具体改动

### 1. Clone mcp-use TypeScript 库
直接克隆到输出目录:
```bash
cd /home/ubuntu/dispatch/infrastructure/tasks/S07-oyster-mcp-typescript/output
git clone https://github.com/mcp-use/mcp-use.git
ls -la mcp-use/libraries/typescript/packages/
```

### 2. 创建 oyster-mcp-ts 项目
```bash
cd /home/ubuntu/dispatch/infrastructure/tasks/S07-oyster-mcp-typescript/output
mkdir -p oyster-mcp-ts/packages/core/src
mkdir -p oyster-mcp-ts/packages/server/src
mkdir -p oyster-mcp-ts/packages/inspector/src
mkdir -p oyster-mcp-ts/packages/cli/src

# 复制并重命名包
cp -r mcp-use/libraries/typescript/packages/mcp-use/* oyster-mcp-ts/packages/core/
cp -r mcp-use/libraries/typescript/packages/server/* oyster-mcp-ts/packages/server/
cp -r mcp-use/libraries/typescript/packages/inspector/* oyster-mcp-ts/packages/inspector/
cp -r mcp-use/libraries/typescript/packages/cli/* oyster-mcp-ts/packages/cli/

# 修改 package.json 中的包名
find oyster-mcp-ts -name "package.json" -exec sed -i 's/"name": "@mcp-use\//"name": "@oyster-mcp\//g' {} \;
find oyster-mcp-ts -name "package.json" -exec sed -i 's/mcp-use/oyster-mcp/g' {} \;
find oyster-mcp-ts -name "*.ts" -exec sed -i 's/@mcp-use\//@oyster-mcp\//g' {} \;
find oyster-mcp-ts -name "*.ts" -exec sed -i 's/mcp-use/oyster-mcp/g' {} \;

```
oyster-mcp-ts/
├── packages/
│   ├── core/              # Client + Agent
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── client.ts
│   │   │   ├── agent.ts
│   │   │   └── types.ts
│   │   └── tsconfig.json
│   │
│   ├── server/           # MCP Server 框架
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── server.ts
│   │   │   ├── tool.ts
│   │   │   ├── resource.ts
│   │   │   └── prompt.ts
│   │   └── tsconfig.json
│   │
│   ├── inspector/        # Web Inspector
│   │   ├── package.json
│   │   └── src/
│   │
│   └── cli/              # Build tool
│       ├── package.json
│       └── src/
│
├── package.json          # Root workspace
├── pnpm-workspace.yaml
└── README.md
```

### 2. 核心功能

**@oyster-mcp/core:**
- MCPClient (stdio/HTTP)
- MCPAgent (多 step reasoning)
- Streaming 支持
- OAuth 处理
- Tool control

**@oyster-mcp/server:**
- createMCPServer() 工厂函数
- server.tool() 定义工具
- server.resource() 定义资源
- server.prompt() 定义 prompts
- 自动 Inspector 挂载

**@oyster-mcp/inspector:**
- 独立 Web 调试界面
- 支持 OAuth
- 持久化 session

**@oyster-mcp/cli:**
- npx create-oyster-mcp-app
- Hot reload
- Auto inspector

### 3. Server 示例
```typescript
import { createMCPServer } from "@oyster-mcp/server";

const server = createMCPServer("my-server", {
  version: "1.0.0",
  description: "My custom MCP server",
});

server.tool({
  name: "get_weather",
  description: "Get weather for a city",
  schema: z.object({
    city: z.string().describe("City name"),
  }),
}, async ({ city }) => {
  return text(`Temperature: 72°F in ${city}`);
});

// 自动 Inspector: http://localhost:3000/inspector
server.listen(3000);
```

### 4. Agent 示例
```typescript
import { MCPAgent, MCPClient } from "@oyster-mcp/core";

const config = {
  mcpServers: {
    filesystem: {
      command: "npx",
      args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
    },
  },
};

const client = new MCPClient(config);
const agent = new MCPAgent({ llm, client });
const result = await agent.run("List files in /tmp");
```

### 5. Inspector 使用
```bash
# Standalone
npx @oyster-mcp/inspector --url http://localhost:3000/sse
```

## 验收标准
- [ ] pnpm workspace 正常工作
- [ ] @oyster-mcp/core 可 import
- [ ] @oyster-mcp/server 可创建自定义 server
- [ ] Inspector 自动挂载
- [ ] 示例代码运行成功

## 验证命令
```bash
cd ~/Downloads/oyster-mcp-ts
pnpm install
pnpm build
cd examples/agent && npx tsx index.ts
```

## 不要做
- 不改现有 frontend 代码
- 不发布到 npm (本地使用)
