---
task_id: S08-mcp-backend-integration
project: clawphones-backend
priority: 2
depends_on: ["S06-oyster-mcp-python"]
modifies: []
executor: glm
---

## 目标
在 clawphones-backend 集成 oyster-mcp，支持 MCP Agent 能力

## 约束
- 不破坏现有 API
- MCP 功能作为独立模块
- 配置通过环境变量管理

## 具体改动

### 1. 安装 oyster-mcp
```bash
# 在 backend 虚拟环境
pip install oyster-mcp
# 或本地开发
pip install -e ~/Downloads/oyster-mcp
```

### 2. 创建 MCP 模块
在 backend 添加:
```
src/
└── mcp/
    ├── __init__.py
    ├── client.py      # MCP 客户端管理
    ├── agent.py       # Agent 工厂
    ├── servers.py     # Server 配置
    └── router.py      # MCP 请求路由
```

### 3. 核心功能

**MCPClientManager:**
- 管理多个 MCP Server 连接
- 支持 stdio 和 HTTP 模式
- Session 池管理

**MCPAgentFactory:**
- 根据配置创建 Agent
- 支持自定义 LLM
- Streaming 处理

**ServerConfigs:**
- Playwright (浏览器自动化)
- Filesystem (文件操作)
- Custom servers (业务逻辑)

### 4. API 端点
```python
# POST /api/mcp/agent/run
{
    "prompt": "Find iPhone 15 deals",
    "servers": ["playwright", "search"],
    "model": "gpt-4o"
}

# GET /api/mcp/servers
# 返回可用 MCP servers

# POST /api/mcp/tool/call
{
    "server": "calculator",
    "tool": "add",
    "args": {"a": 5, "b": 3}
}
```

### 5. 配置示例
```python
# config.py
MCP_SERVERS = {
    "playwright": {
        "command": "npx",
        "args": ["-y", "@playwright/mcp@latest"],
        "env": {"DISPLAY": ":1"}
    },
    "filesystem": {
        "command": "npx", 
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    }
}
```

## 验收标准
- [ ] pip install oyster-mcp 成功
- [ ] MCP Agent 可执行任务
- [ ] API 端点正常工作
- [ ] 单元测试通过

## 验证命令
```bash
cd ~/Downloads/clawphones-backend
source venv/bin/activate
pip install -e ~/Downloads/oyster-mcp
pytest tests/mcp/
```

## 不要做
- 不删除现有 API
- 不修改数据库 schema
- 不提交 secrets 到 git
