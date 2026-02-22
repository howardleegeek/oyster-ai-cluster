---
task_id: S85-anvil-manager-tool
project: shell
priority: 2
estimated_minutes: 25
depends_on: ["S71-mcp-server-scaffold"]
modifies: ["mcp-server/src/tools/anvil-manager.ts", "mcp-server/src/server.ts"]
executor: glm
---

## 目标

实现 `anvil_manager` MCP 工具，一键启动/停止/重置 Anvil 本地链。

## 背景

用户不应该手动启动 Anvil。当 AI 需要部署或测试时，应该能自动确保 Anvil 在运行。这消除了"先跑 anvil"的步骤。

## 步骤

1. 创建 `mcp-server/src/tools/anvil-manager.ts`:
   ```typescript
   name: "anvil_manager"
   description: "Start, stop, or reset the local Anvil blockchain."
   inputSchema: {
     action: "start" | "stop" | "reset" | "status",
     options?: {
       block_time?: number,      // 出块间隔秒数 (default: 1)
       accounts?: number,        // 账户数 (default: 10)
       balance?: number,         // 初始余额 ETH (default: 10000)
       fork_url?: string,        // Fork 主网/测试网
       fork_block?: number       // Fork 的区块高度
     }
   }
   ```
2. 实现:
   - `start`: 后台 spawn anvil, 记录 PID, 等待就绪
   - `stop`: kill Anvil 进程
   - `reset`: stop + start (清除所有状态)
   - `status`: 返回运行状态 + 链信息
   - Fork 模式: `anvil --fork-url {url} --fork-block-number {block}`
3. 返回:
   ```typescript
   {
     running: boolean,
     pid?: number,
     rpc_url: "http://127.0.0.1:8545",
     chain_id: 31337,
     accounts: [{ address, private_key, balance }],
     forked_from?: string
   }
   ```

## 约束

- 同时只能运行一个 Anvil 实例
- 启动超时: 10 秒
- 必须在 stop/reset 时完全清理进程

## 验收标准

- [ ] start → status 显示 running
- [ ] reset 后区块高度回到 0
- [ ] fork 模式可以 fork Ethereum mainnet
- [ ] stop 后端口 8545 释放

## 不要做

- 不要修改 web-ui/
- 不要支持多个 Anvil 实例
