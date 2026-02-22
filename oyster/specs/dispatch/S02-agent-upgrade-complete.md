---
task_id: S02-agent-upgrade-complete
project: dispatch
priority: 1
depends_on: []
modifies: ["dispatch/slot_agent.py", "dispatch/dispatch.py", "dispatch/memory.py", "dispatch/agent_comm.py", "dispatch/agent_mcp.py"]
executor: glm
---

## 目标
全面升级 Agent 系统：通信 + 记忆 + 验证 + 浏览器集成 + MCP Server

## 约束
- 不破坏现有 dispatch 机制
- 向后兼容现有任务
- 浏览器能力复用已有 browsermcp_api.py

## 具体改动

### 1. Agent 通信系统 (agent_comm.py)
Agent 之间能相互协作：
- `post_message(agent_id, message)` - 发送消息到指定 Agent
- `broadcast_message(message)` - 广播消息到所有 Agent
- `receive_messages()` - 接收待处理消息
- `delegate_task(agent_id, task_spec)` - 委托任务给其他 Agent
- 消息队列存储在 ~/dispatch/agent_mailbox/
- 消息格式: {from, to, subject, body, timestamp, status}

### 2. Memory 系统 (memory.py)
跨任务上下文记忆：
- `store(key, value, ttl=86400)` - 存储记忆 (默认 24 小时)
- `recall(key)` - 召回记忆
- `search(query)` - 搜索记忆
- `forget(key)` - 删除记忆
- `get_context()` - 获取当前任务相关上下文
- 存储在 ~/dispatch/memory/ (JSON 文件)
- 支持任务链记忆继承

### 3. Collect 验证 (dispatch.py 增强)
收集后自动构建测试：
- `collect_and_validate(project)` - 收集 + 构建 + 测试
- 自动检测项目类型 (Node/Python/Go)
- 运行对应构建命令 (npm build / make / go build)
- 运行测试 (npm test / pytest / go test)
- 生成验证报告
- 失败自动回滚

### 4. 浏览器 MCP 集成
复用已有 browsermcp_api.py：
- 创建 browser_bridge.py 桥接
- Slot Agent 可调用本地浏览器
- 支持 CDP 远程连接
- 视觉验证能力集成

### 5. Agent MCP Server (agent_mcp.py)
暴露工具 via MCP 协议：
- 标准 MCP tools 接口
- 动态工具注册
- 支持 stdio 和 HTTP 模式
- 暴露 slot_agent 核心能力:
  - execute_task
  - get_status
  - browse_page
  - run_test
  - store_memory
  - recall_memory
  - delegate_to_agent

### 6. 升级 slot_agent.py
集成以上所有能力：
```python
class SlotAgent:
    def __init__(self, ...):
        # 新增能力
        self.memory = AgentMemory()
        self.comm = AgentComm(self.agent_id)
        self.mcp = None  # 按需初始化
        
    def delegate_task(self, target_agent, spec):
        """委托任务给其他 Agent"""
        
    def share_context(self, other_agent_id):
        """共享上下文记忆"""
        
    def validate_and_collect(self, project):
        """收集 + 验证"""
```

## 验收标准
- [ ] Agent 之间能发送/接收消息
- [ ] 任务能委托给其他 Agent
- [ ] Memory 能跨任务保持
- [ ] Collect 能自动构建测试
- [ ] Browser MCP 桥接可用
- [ ] Agent MCP Server 可启动
- [ ] 同步到所有节点

## 不要做
- 不修改 task-watcher
- 不修改 guardian
- 不改动 nodes.json
