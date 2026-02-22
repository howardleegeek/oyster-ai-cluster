---
task_id: S09-bridge-daemon
project: dispatch
priority: 1
depends_on: []
modifies: ["dispatch/bridge.py", "dispatch/bridge-daemon.py", "Library/LaunchAgents/com.oyster.bridge-daemon.plist"]
executor: glm
---

# Bridge Daemon v2 — Opus↔OpenCode 双向可靠通讯

## 背景
当前 bridge.py 是纯 pull 模式。Opus 能 send，但 OpenCode 没有后台进程轮询 recv，消息写进 SQLite 后永远没人读。需要一个常驻 daemon 让消息真正可靠双向传递。

## 目标
让 Opus send 到 bridge 的消息，OpenCode 能在 5 秒内自动收到并执行。反之亦然。

## 方案：bridge-daemon.py (常驻轮询 + 动作执行)

### 1. 新文件: `dispatch/bridge-daemon.py`
```
功能:
- 常驻后台运行，每 2 秒轮询 bridge.db 中 recipient=opencode 且 read_at IS NULL 的消息
- 收到消息后，根据 msg_type 执行对应动作:
  - "chat": 调用 opencode run "<payload.text>" 执行任务
  - "command": 解析 payload.action，执行对应 dispatch 命令
  - "ping": 自动回复 pong (reply_to = 原消息 id)
  - "spec": 将 payload 写入 specs/ 目录，然后跑 dispatch start
- 执行完成后，通过 bridge.send() 把结果回传给 sender
- 所有执行记录写日志: dispatch/bridge-daemon.log
- PID 文件: dispatch/bridge-daemon.pid (用于 launchd 管理)
- 异常捕获: 单条消息执行失败不影响 daemon 运行，错误写回 bridge 作为 error 类型消息

架构:
- main loop: while True → bridge.recv(timeout=2) → dispatch_message(msg) → bridge.send(reply)
- dispatch_message(): match msg_type → 调用对应 handler
- handler_chat(): subprocess.run(["opencode", "run", text], capture_output=True, timeout=300)
- handler_command(): 解析并执行 dispatch.py 命令
- handler_ping(): bridge.send(sender, "pong", {}, reply_to=msg_id)
- handler_spec(): 写文件 + 调 dispatch start

安全约束:
- 只接受 msg_type in ["chat", "command", "ping", "spec"]，其他忽略并告警
- 单条消息执行超时 5 分钟
- 不执行任何 shell 注入 (payload 不能直接拼 shell 命令，只走预定义 handler)
```

### 2. 修改: `dispatch/bridge.py`
```
新增:
- Bridge.send() 返回值不变
- 新增 Bridge.unread_count(recipient) 方法: 返回未读消息数
- 新增 CLI 命令: bridge.py unread <identity> — 快速检查有没有未读消息
- 新增 CLI 命令: bridge.py daemon — 等同于启动 bridge-daemon.py (便捷入口)
```

### 3. 新文件: `~/Library/LaunchAgents/com.oyster.bridge-daemon.plist`
```
launchd 配置:
- Label: com.oyster.bridge-daemon
- ProgramArguments: ["/usr/bin/python3", "/Users/howardli/Downloads/dispatch/bridge-daemon.py"]
- RunAtLoad: true
- KeepAlive: true (崩溃自动重启)
- StandardOutPath: /Users/howardli/Downloads/dispatch/logs/bridge-daemon-stdout.log
- StandardErrorPath: /Users/howardli/Downloads/dispatch/logs/bridge-daemon-stderr.log
- WorkingDirectory: /Users/howardli/Downloads/dispatch
```

## 约束
- 不修改 bridge.db schema (兼容现有消息)
- 不修改 dispatch.py
- 不修改 SSH 连接层
- 不修改 guardian.py
- Python 3.13+ (Mac 自带)，不引入新依赖
- daemon 必须优雅关闭 (SIGTERM handler)

## 验收标准
- [ ] `bridge-daemon.py` 启动后，Opus 发的 ping 在 5s 内收到 pong
- [ ] Opus 发 chat 消息，OpenCode 自动执行并回传结果
- [ ] daemon 崩溃后 launchd 10s 内自动重启
- [ ] `bridge.py unread opencode` 正确返回未读数
- [ ] 日志记录所有消息处理 (时间戳 + msg_id + 结果)
- [ ] 单条消息失败不影响后续消息处理

## 不要做
- 不要改 dispatch.py / task-wrapper.sh / nodes.json
- 不要改 SSH 连接层
- 不要引入 Redis/RabbitMQ 等外部依赖
- 不要改 bridge.db 的 schema
