---
task_id: S06-oyster-mcp-python
project: infrastructure
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
基于 mcp-use 核心能力，创建 oyster-mcp Python 包 - 支持 MCP Client 和 MCP Agent

## 约束
- 不改现有项目代码
- 直接 fork/adopt mcp-use 的核心实现
- 保持 MIT 协议开源

## 具体改动

### 1. Clone mcp-use Python 库
直接克隆到当前工作目录 (不要用 ~/Downloads):
```bash
cd /home/ubuntu/dispatch/infrastructure/tasks/S06-oyster-mcp-python/output
git clone https://github.com/mcp-use/mcp-use.git
# 查看 Python 库结构
ls -la mcp-use/libraries/python/
```

### 2. 创建 oyster-mcp 项目
在 output 目录创建项目:
```bash
cd /home/ubuntu/dispatch/infrastructure/tasks/S06-oyster-mcp-python/output
mkdir -p oyster-mcp/src/oyster_mcp
mkdir -p oyster-mcp/examples
mkdir -p oyster-mcp/tests
# 复制并重命名
cp -r mcp-use/libraries/python/mcp_use/* oyster-mcp/src/oyster_mcp/
# 修改包名: 把所有 mcp_use 替换为 oyster_mcp
find oyster-mcp/src/oyster_mcp -name "*.py" -exec sed -i 's/mcp_use/oyster_mcp/g' {} \;
find oyster-mcp/src/oyster_mcp -name "*.py" -exec sed -i 's/mcp-use/oyster-mcp/g' {} \;

### 3. 创建 pyproject.toml
在 `~/Downloads/oyster-mcp/pyproject.toml`:

```toml
[project]
name = "oyster-mcp"
version = "0.1.0"
description = "Oyster Labs MCP Client and Agent"
requires-python = ">=3.10"
dependencies = [
    "mcp>=1.0.0",
    "langchain>=0.1.0",
    "langchain-openai>=0.0.5",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio"]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

```
oyster-mcp/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── oyster_mcp/
│       ├── __init__.py
│       ├── client.py      # MCPClient
│       ├── agent.py       # MCPAgent
│       ├── config.py      # 配置管理
│       └── types.py       # 类型定义
├── examples/
│   ├── agent_example.py
│   └── client_example.py
└── tests/
```

### 7. 复制回本地
任务完成后，output 目录的文件会被自动同步回本地:
```
/Users/howardli/Downloads/dispatch/output/infrastructure/S06-oyster-mcp-python/
```

确认文件存在后，手动复制到目标位置:
```bash
cp -r /Users/howardli/Downloads/dispatch/output/infrastructure/S06-oyster-mcp-python/output/oyster-mcp /Users/howardli/Downloads/
```

```python
import asyncio
import os
from langchain_openai import ChatOpenAI
from oyster_mcp import MCPAgent, MCPClient

async def main():
    # 配置 MCP server
    config = {
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
            }
        }
    }
    
    client = MCPClient.from_dict(config)
    await client.create_all_sessions()
    
    # 使用 OpenAI
    llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
    agent = MCPAgent(llm=llm, client=client)
    
    result = await agent.run("List files in /tmp")
    print(result)
    
    await client.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(main())
```

**MCPClient** - 支持:
- from_dict() 配置创建
- stdio 连接 (npx 命令)
- HTTP 连接 (远程服务器)
- 多 server 动态选择
- OAuth 处理
- 直接 call_tool()

**MCPAgent** - 支持:
- LangChain 兼容 LLM
- 多 step reasoning
- Streaming 输出
- Tool control (限制访问)
- Langfuse 可观测性集成

### 3. 配置示例
```python
config = {
    "mcpServers": {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
        },
        "playwright": {
            "command": "npx", 
            "args": ["-y", "@playwright/mcp@latest"],
            "env": {"DISPLAY": ":1"}
        }
    }
}
```

### 4. 示例代码

**Agent 示例:**
```python
from oyster_mcp import MCPAgent, MCPClient

client = MCPClient.from_dict(config)
llm = ChatOpenAI(model="gpt-4o")
agent = MCPAgent(llm=llm, client=client)
result = await agent.run("List files in /tmp")
```

**Client 直接调用:**
```python
client = MCPClient.from_dict(config)
session = client.get_session("calculator")
result = await session.call_tool("add", {"a": 5, "b": 3})
```

## 验收标准
- [ ] pyproject.toml 正确配置，可 `pip install -e .` 安装
- [ ] MCPClient 可连接 stdio server (filesystem)
- [ ] MCPAgent 可执行多 step 任务
- [ ] 示例代码运行成功
- [ ] 类型提示完整

## 验证命令
```bash
cd ~/Downloads/oyster-mcp
pip install -e .
python examples/agent_example.py
```

## 不要做
- 不修改现有 clawphones-backend 代码
- 不提交到 PyPI (本地使用)
