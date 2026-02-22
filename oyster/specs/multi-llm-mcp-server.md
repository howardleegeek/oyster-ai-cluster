# Multi-LLM MCP Server Spec

> 在 Claude Code 里通过 MCP 工具直接调用 MiniMax M2.5 和 GLM-5 作为完整 Agent

## 目标

一个 MCP server，暴露两个 LLM 后端（MiniMax M2.5 + GLM-5），支持完整 agent 能力：
- 对话（chat completion）
- 工具调用（function calling / tool use）
- 文件读写（通过内置工具）
- 代码执行（通过内置 shell 工具）
- 流式输出

Claude Code 里的调用方式：
```
mcp__llm__minimax "设计缓存架构"
mcp__llm__glm "生成 CRUD 代码"
mcp__llm__chat --model minimax "任务"
```

---

## 架构

```
Claude Code CLI
  │
  ├── MCP Protocol (stdio)
  │
  └── multi-llm-mcp-server (Node.js / TypeScript)
        │
        ├── Tool: chat        → 发送 prompt 到指定模型，返回回复
        ├── Tool: agent_run   → 完整 agent loop（对话 + 工具调用 + 多轮）
        │
        ├── Backend: MiniMax M2.5
        │     └── OpenAI-compatible API (api.minimax.io/v1)
        │
        └── Backend: GLM-5
              └── Anthropic-compatible API (api.z.ai/api/anthropic)
```

---

## MCP Tools (暴露给 Claude Code)

### Tool 1: `chat`

简单对话，单轮 prompt → response。

```json
{
  "name": "chat",
  "description": "Send a prompt to MiniMax or GLM and get a response",
  "inputSchema": {
    "type": "object",
    "properties": {
      "model": {
        "type": "string",
        "enum": ["minimax", "glm"],
        "description": "Which LLM backend to use"
      },
      "prompt": {
        "type": "string",
        "description": "The prompt to send"
      },
      "system": {
        "type": "string",
        "description": "Optional system prompt"
      },
      "temperature": {
        "type": "number",
        "default": 0.7
      },
      "max_tokens": {
        "type": "number",
        "default": 4096
      }
    },
    "required": ["model", "prompt"]
  }
}
```

### Tool 2: `agent_run`

完整 agent loop：模型可以调用内置工具（文件读写、shell 执行、搜索），多轮自动运行直到完成。

```json
{
  "name": "agent_run",
  "description": "Run a full agent loop with MiniMax or GLM. The agent can read/write files, execute shell commands, and search code. It runs autonomously until the task is complete.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "model": {
        "type": "string",
        "enum": ["minimax", "glm"],
        "description": "Which LLM backend to use"
      },
      "task": {
        "type": "string",
        "description": "The task for the agent to complete"
      },
      "cwd": {
        "type": "string",
        "description": "Working directory for file operations and shell commands"
      },
      "max_turns": {
        "type": "number",
        "default": 20,
        "description": "Maximum agent turns before stopping"
      },
      "system": {
        "type": "string",
        "description": "Optional system prompt override"
      }
    },
    "required": ["model", "task"]
  }
}
```

### Tool 3: `list_models`

列出可用模型和状态。

```json
{
  "name": "list_models",
  "description": "List available LLM backends and their status",
  "inputSchema": {
    "type": "object",
    "properties": {}
  }
}
```

---

## Agent 内置工具 (模型可调用)

agent_run 模式下，模型可以调用以下工具：

| 工具 | 描述 | 参数 |
|------|------|------|
| `read_file` | 读取文件内容 | `path`, `offset?`, `limit?` |
| `write_file` | 写入文件 | `path`, `content` |
| `edit_file` | 编辑文件（替换） | `path`, `old_string`, `new_string` |
| `shell` | 执行 shell 命令 | `command`, `cwd?`, `timeout?` |
| `glob` | 文件名搜索 | `pattern`, `path?` |
| `grep` | 内容搜索 | `pattern`, `path?`, `glob?` |

这些工具在 server 侧实现，模型通过 function calling 调用。

---

## API 后端配置

### MiniMax M2.5 (OpenAI-compatible)

```typescript
{
  name: "minimax",
  type: "openai-compatible",
  baseUrl: "https://api.minimax.io/v1",
  model: "MiniMax-M2.5",
  apiKeyEnv: "MINIMAX_API_KEY",
  // Chat endpoint: POST /chat/completions
  // Supports: tools, streaming, temperature, max_tokens
}
```

### GLM-5 (Anthropic-compatible)

```typescript
{
  name: "glm",
  type: "anthropic-compatible",
  baseUrl: "https://api.z.ai/api/anthropic",
  model: "glm-5",  // or latest available
  apiKeyEnv: "ZAI_API_KEY",
  // Uses Anthropic Messages API format
  // Supports: tools, streaming, temperature, max_tokens
}
```

---

## 实现细节

### 技术栈
- **语言**: TypeScript (Node.js)
- **MCP SDK**: `@modelcontextprotocol/sdk` ^1.23.0
- **Transport**: stdio (Claude Code 标准模式)
- **依赖**: `zod` (验证), `openai` (MiniMax API), `@anthropic-ai/sdk` (GLM API)

### 文件结构

```
~/Downloads/multi-llm-mcp/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts              # CLI 入口
│   ├── server.ts             # MCP Server 主类
│   ├── backends/
│   │   ├── types.ts          # 统一 LLM 接口
│   │   ├── minimax.ts        # MiniMax M2.5 OpenAI-compatible 后端
│   │   └── glm.ts            # GLM Anthropic-compatible 后端
│   ├── tools/
│   │   ├── chat.ts           # chat tool
│   │   ├── agent.ts          # agent_run tool (agent loop 逻辑)
│   │   └── list-models.ts    # list_models tool
│   └── agent-tools/
│       ├── read-file.ts      # Agent 内置: 读文件
│       ├── write-file.ts     # Agent 内置: 写文件
│       ├── edit-file.ts      # Agent 内置: 编辑文件
│       ├── shell.ts          # Agent 内置: 执行命令
│       ├── glob.ts           # Agent 内置: 文件搜索
│       └── grep.ts           # Agent 内置: 内容搜索
└── dist/                     # 编译输出
```

### 统一 LLM 接口

```typescript
interface LLMBackend {
  name: string;

  // 简单对话
  chat(params: {
    messages: Message[];
    temperature?: number;
    max_tokens?: number;
  }): Promise<string>;

  // 带工具调用的对话（返回文本或工具调用）
  chatWithTools(params: {
    messages: Message[];
    tools: ToolDefinition[];
    temperature?: number;
    max_tokens?: number;
  }): Promise<LLMResponse>;

  // 健康检查
  healthCheck(): Promise<boolean>;
}

type LLMResponse =
  | { type: "text"; content: string }
  | { type: "tool_calls"; calls: ToolCall[] };

interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
}
```

### Agent Loop 逻辑

```
agent_run(task, model, cwd, max_turns):
  messages = [system_prompt, user_task]
  for turn in 1..max_turns:
    response = backend.chatWithTools(messages, agent_tools)
    if response.type == "text":
      return response.content  // 任务完成
    if response.type == "tool_calls":
      for call in response.calls:
        result = execute_agent_tool(call.name, call.arguments, cwd)
        messages.append(tool_result(call.id, result))
  return "达到最大轮次限制"
```

### 安全约束

- `shell` 工具默认 timeout 120s
- `write_file` / `edit_file` 仅限 `cwd` 及其子目录
- 禁止写入 `~/.oyster-keys/`, `~/.ssh/`, `~/.claude/` 等敏感目录
- Agent loop 最大 20 轮（可配置）
- API key 从环境变量读取，不硬编码

---

## Claude Code 注册配置

部署后在 `~/.claude.json` 添加：

```json
{
  "mcpServers": {
    "llm": {
      "type": "stdio",
      "command": "node",
      "args": ["/Users/howardli/Downloads/multi-llm-mcp/dist/index.js"],
      "env": {
        "MINIMAX_API_KEY": "<from ~/.oyster-keys/minimax.env>",
        "ZAI_API_KEY": "<from ~/.oyster-keys/zai-glm.env>"
      }
    }
  }
}
```

或者用 source 脚本加载 env：

```json
{
  "mcpServers": {
    "llm": {
      "type": "stdio",
      "command": "bash",
      "args": [
        "-c",
        "source ~/.oyster-keys/minimax.env && source ~/.oyster-keys/zai-glm.env && node /Users/howardli/Downloads/multi-llm-mcp/dist/index.js"
      ]
    }
  }
}
```

---

## 验收标准

1. `mcp__llm__chat --model minimax "hello"` → 返回 MiniMax 回复
2. `mcp__llm__chat --model glm "hello"` → 返回 GLM 回复
3. `mcp__llm__agent_run --model minimax --task "读取 package.json 并总结"` → 模型调用 read_file，返回总结
4. `mcp__llm__agent_run --model glm --task "创建 hello.py 并运行"` → 模型调用 write_file + shell，返回结果
5. `mcp__llm__list_models` → 返回两个模型状态
6. Agent loop 不超过 max_turns
7. 文件操作不逃逸 cwd

---

## 预估

- **代码量**: ~600 行 TypeScript
- **执行者**: GLM 或 MiniMax
- **时间**: ~30 分钟（单节点）
