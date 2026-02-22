---
task_id: S08-mcp-frontend-integration
project: frontend
priority: 2
depends_on: ["S07-oyster-mcp-typescript"]
modifies: []
executor: glm
---

## 目标
在 frontend (Next.js) 集成 oyster-mcp-ts，支持 MCP Agent 和 Server

## 约束
- 不破坏现有 UI
- MCP 作为独立组件
- 配置通过环境变量管理

## 具体改动

### 1. 安装
```bash
cd ~/Downloads/frontend
pnpm add @oyster-mcp/core @oyster-mcp/server
# 本地开发
pnpm add -D @oyster-mcp/core@link:../oyster-mcp-ts/packages/core
```

### 2. 创建 MCP 组件库
```
src/
├── components/
│   └── mcp/
│       ├── MCPClientPanel.tsx    # Client 配置面板
│       ├── MCPAgentChat.tsx      # Agent 对话界面
│       ├── MCPServerList.tsx     # Server 列表
│       └── MCPInspectorButton.tsx # 打开 Inspector
│
├── lib/
│   └── mcp/
│       ├── client.ts             # MCP 客户端
│       ├── agent.ts              # Agent 封装
│       └── config.ts             # 配置
│
└── app/
    └── api/
        └── mcp/
            └── route.ts          # MCP API 代理
```

### 3. 核心组件

**MCPClientPanel:**
- Server 配置 UI
- 连接状态显示
- 重连按钮

**MCPAgentChat:**
- Chat 界面
- Streaming 响应
- Tool 调用显示

**MCPInspectorButton:**
- 打开 Inspector 的按钮
- 支持 embed 模式

### 4. 使用示例
```typescript
// app/mcp/page.tsx
"use client";
import { MCPAgent, MCPClient } from "@oyster-mcp/core";

export default function MCPPage() {
  const [result, setResult] = useState("");
  
  const runAgent = async () => {
    const client = new MCPClient(config);
    const agent = new MCPAgent({ llm, client });
    const result = await agent.run("Find iPhone prices");
    setResult(result);
  };
  
  return (
    <div>
      <button onClick={runAgent}>Run Agent</button>
      <pre>{result}</pre>
    </div>
  );
}
```

### 5. API 路由
```typescript
// app/api/mcp/agent/route.ts
import { MCPAgent, MCPClient } from "@oyster-mcp/core";

export async function POST(req: Request) {
  const { prompt, servers } = await req.json();
  const client = new MCPClient(buildConfig(servers));
  const agent = new MCPAgent({ llm, client });
  const result = await agent.run(prompt);
  return Response.json({ result });
}
```

## 验收标准
- [ ] pnpm install 成功
- [ ] MCP 组件可正常渲染
- [ ] Agent 可执行任务
- [ ] Inspector 按钮工作

## 验证命令
```bash
cd ~/Downloads/frontend
pnpm build
pnpm dev
# 访问 /mcp 测试
```

## 不要做
- 不修改现有页面
- 不改变路由结构
