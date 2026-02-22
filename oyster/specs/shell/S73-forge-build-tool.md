---
task_id: S73-forge-build-tool
project: shell
priority: 2
estimated_minutes: 30
depends_on: ["S71-mcp-server-scaffold"]
modifies: ["mcp-server/src/tools/forge-build.ts", "mcp-server/src/server.ts"]
executor: glm
---

## 目标

实现 `forge_build` MCP 工具，能编译 Solidity 合约并返回 ABI + bytecode。

## 步骤

1. 创建 `mcp-server/src/tools/forge-build.ts`:
   ```typescript
   name: "forge_build"
   description: "Compile Solidity contracts using Foundry. Returns ABI and bytecode."
   inputSchema: {
     project_dir: string,       // Foundry 项目目录
     contract_name?: string,    // 可选: 只编译特定合约
     optimize?: boolean,        // 是否开启优化 (default: true)
     optimize_runs?: number     // 优化轮数 (default: 200)
   }
   ```
2. 执行 `forge build --json` 子进程
3. 解析输出:
   - 成功: 返回 `{ success: true, contracts: [{ name, abi, bytecode, deployedBytecode }] }`
   - 失败: 返回 `{ success: false, errors: [{ file, line, message, severity }] }`
4. 在 server.ts 注册工具

## 约束

- ABI 返回 JSON 格式 (不是 ABI-encoded)
- bytecode 返回 hex 字符串
- 编译错误必须包含文件名和行号

## 验收标准

- [ ] 编译成功时返回 ABI + bytecode
- [ ] 编译失败时返回具体错误位置和信息
- [ ] 可选 contract_name 过滤只返回指定合约

## 不要做

- 不要修改 web-ui/
- 不要安装 Forge
