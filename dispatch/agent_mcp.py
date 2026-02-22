#!/usr/bin/env python3
"""
Agent MCP Server - 暴露 Agent 能力 via MCP 协议

功能:
- 标准 MCP tools 接口
- 动态工具注册
- 支持 stdio 和 HTTP 模式
- 暴露 slot_agent 核心能力
"""

import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# 配置
DISPATCH_DIR = Path.home() / "dispatch"


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [AgentMCP] {msg}", flush=True)


@dataclass
class MCPTool:
    """MCP 工具定义"""

    name: str
    description: str
    input_schema: Dict


@dataclass
class MCPRequest:
    """MCP 请求"""

    jsonrpc: str = "2.0"
    id: Any = None
    method: str = ""
    params: Dict = None


@dataclass
class MCPResponse:
    """MCP 响应"""

    jsonrpc: str = "2.0"
    id: Any = None
    result: Any = None
    error: Dict = None


class AgentMCPServer:
    """Agent MCP Server"""

    def __init__(self, agent_id: str = "dispatch-agent"):
        self.agent_id = agent_id
        self.tools: List[MCPTool] = []
        self._register_tools()

    def _register_tools(self):
        """注册可用工具"""
        self.tools = [
            MCPTool(
                name="execute_task",
                description="Execute a task on the dispatch system",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project": {"type": "string", "description": "Project name"},
                        "spec_file": {
                            "type": "string",
                            "description": "Spec file path",
                        },
                    },
                    "required": ["project"],
                },
            ),
            MCPTool(
                name="get_status",
                description="Get current agent status",
                input_schema={
                    "type": "object",
                    "properties": {
                        "agent_id": {"type": "string", "description": "Agent ID"},
                    },
                },
            ),
            MCPTool(
                name="browse_page",
                description="Browse a webpage and get snapshot",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to browse"},
                        "wait": {"type": "number", "description": "Wait seconds"},
                    },
                    "required": ["url"],
                },
            ),
            MCPTool(
                name="run_test",
                description="Run tests for a project",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project": {"type": "string", "description": "Project name"},
                        "test_cmd": {"type": "string", "description": "Test command"},
                    },
                    "required": ["project"],
                },
            ),
            MCPTool(
                name="store_memory",
                description="Store information in agent memory",
                input_schema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Memory key"},
                        "value": {"type": "string", "description": "Memory value"},
                        "ttl": {
                            "type": "number",
                            "description": "Time to live (seconds)",
                        },
                    },
                    "required": ["key", "value"],
                },
            ),
            MCPTool(
                name="recall_memory",
                description="Recall information from agent memory",
                input_schema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Memory key"},
                    },
                    "required": ["key"],
                },
            ),
            MCPTool(
                name="search_memory",
                description="Search agent memory",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                    },
                    "required": ["query"],
                },
            ),
            MCPTool(
                name="delegate_to_agent",
                description="Delegate task to another agent",
                input_schema={
                    "type": "object",
                    "properties": {
                        "target_agent": {
                            "type": "string",
                            "description": "Target agent ID",
                        },
                        "task_spec": {
                            "type": "object",
                            "description": "Task specification",
                        },
                    },
                    "required": ["target_agent", "task_spec"],
                },
            ),
            MCPTool(
                name="send_message",
                description="Send message to another agent",
                input_schema={
                    "type": "object",
                    "properties": {
                        "to_agent": {
                            "type": "string",
                            "description": "Target agent ID",
                        },
                        "subject": {"type": "string", "description": "Message subject"},
                        "body": {"type": "string", "description": "Message body"},
                    },
                    "required": ["to_agent", "subject"],
                },
            ),
            MCPTool(
                name="list_agents",
                description="List all available agents",
                input_schema={
                    "type": "object",
                    "properties": {},
                },
            ),
        ]

    def handle_request(self, request: MCPRequest) -> MCPResponse:
        """处理 MCP 请求"""
        method = request.method

        try:
            if method == "tools/list":
                result = {
                    "tools": [
                        {
                            "name": t.name,
                            "description": t.description,
                            "inputSchema": t.input_schema,
                        }
                        for t in self.tools
                    ]
                }
                return MCPResponse(id=request.id, result=result)

            elif method == "tools/call":
                tool_name = request.params.get("name")
                args = request.params.get("arguments", {})
                result = self._call_tool(tool_name, args)
                return MCPResponse(id=request.id, result=result)

            elif method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "dispatch-agent",
                        "version": "1.0.0",
                    },
                    "capabilities": {
                        "tools": True,
                    },
                }
                return MCPResponse(id=request.id, result=result)

            else:
                return MCPResponse(
                    id=request.id,
                    error={"code": -32601, "message": f"Method not found: {method}"},
                )

        except Exception as e:
            log(f"Error handling {method}: {e}")
            return MCPResponse(
                id=request.id,
                error={"code": -32603, "message": str(e)},
            )

    def _call_tool(self, tool_name: str, args: Dict) -> Dict:
        """调用工具"""
        log(f"Calling tool: {tool_name} with args: {args}")

        if tool_name == "execute_task":
            # 调用 dispatch 执行任务
            return {"status": "not_implemented", "message": "Use dispatch.py CLI"}

        elif tool_name == "get_status":
            # 返回 agent 状态
            return {
                "agent_id": self.agent_id,
                "status": "running",
                "tools_count": len(self.tools),
            }

        elif tool_name == "browse_page":
            # 浏览页面
            url = args.get("url")
            wait = args.get("wait", 1)

            # 尝试使用 browser_bridge
            try:
                from dispatch.browser_bridge import BrowserBridge

                browser = BrowserBridge()
                browser.navigate(url)
                browser.wait(wait)
                snapshot = browser.screenshot()
                return {"url": url, "snapshot": snapshot[:500] if snapshot else ""}
            except Exception as e:
                return {"error": str(e), "url": url}

        elif tool_name == "run_test":
            # 运行测试
            import subprocess

            project = args.get("project")
            test_cmd = args.get("test_cmd", "npm test")

            project_dir = DISPATCH_DIR / project
            if project_dir.exists():
                result = subprocess.run(
                    test_cmd.split(),
                    cwd=str(project_dir),
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                return {
                    "project": project,
                    "cmd": test_cmd,
                    "exit_code": result.returncode,
                    "output": result.stdout + result.stderr,
                }
            return {"error": "Project not found"}

        elif tool_name == "store_memory":
            # 存储记忆
            from dispatch.memory import AgentMemory

            memory = AgentMemory(self.agent_id)
            memory.store(args.get("key"), args.get("value"), args.get("ttl", 86400))
            return {"status": "stored", "key": args.get("key")}

        elif tool_name == "recall_memory":
            # 召回记忆
            from dispatch.memory import AgentMemory

            memory = AgentMemory(self.agent_id)
            value = memory.recall(args.get("key"))
            return {"key": args.get("key"), "value": value}

        elif tool_name == "search_memory":
            # 搜索记忆
            from dispatch.memory import AgentMemory

            memory = AgentMemory(self.agent_id)
            results = memory.search(args.get("query"))
            return {"query": args.get("query"), "results": results}

        elif tool_name == "delegate_to_agent":
            # 委托任务
            from dispatch.agent_comm import AgentComm

            comm = AgentComm(self.agent_id)
            comm.delegate_task(args.get("target_agent"), args.get("task_spec"))
            return {"status": "delegated", "to": args.get("target_agent")}

        elif tool_name == "send_message":
            # 发送消息
            from dispatch.agent_comm import AgentComm

            comm = AgentComm(self.agent_id)
            comm.post_message(
                args.get("to_agent"),
                args.get("subject"),
                args.get("body", ""),
            )
            return {"status": "sent", "to": args.get("to_agent")}

        elif tool_name == "list_agents":
            # 列出所有 Agent
            from dispatch.agent_comm import list_all_agents

            return {"agents": list_all_agents()}

        return {"error": f"Unknown tool: {tool_name}"}


def run_stdio_server():
    """运行 stdio 模式服务器"""
    server = AgentMCPServer()

    while True:
        try:
            line = input()
            if not line.strip():
                continue

            request_data = json.loads(line)
            request = MCPRequest(**request_data)
            response = server.handle_request(request)

            print(
                json.dumps(
                    {
                        "jsonrpc": response.jsonrpc,
                        "id": response.id,
                        "result": response.result,
                        "error": response.error,
                    }
                ),
                flush=True,
            )

        except EOFError:
            break
        except Exception as e:
            log(f"Error: {e}")


def run_http_server(host: str = "127.0.0.1", port: int = 8080):
    """运行 HTTP 模式服务器"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import urllib.parse

    server = AgentMCPServer()

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            request_data = json.loads(body)

            request = MCPRequest(**request_data)
            response = server.handle_request(request)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {
                        "jsonrpc": response.jsonrpc,
                        "id": response.id,
                        "result": response.result,
                        "error": response.error,
                    }
                ).encode()
            )

        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"ok": True, "server": "agent-mcp"}).encode()
                )
            else:
                self.send_response(404)
                self.end_headers()

    httpd = HTTPServer((host, port), Handler)
    log(f"HTTP server started on {host}:{port}")
    httpd.serve_forever()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Agent MCP Server")
    parser.add_argument("--stdio", action="store_true", help="Run in stdio mode")
    parser.add_argument("--http", action="store_true", help="Run in HTTP mode")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--agent-id", default="dispatch-agent")

    args = parser.parse_args()

    if args.stdio:
        run_stdio_server()
    elif args.http:
        run_http_server(args.host, args.port)
    else:
        # 默认运行 HTTP
        run_http_server(args.host, args.port)


if __name__ == "__main__":
    main()
