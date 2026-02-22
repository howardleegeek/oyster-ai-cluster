---
task_id: S72-forge-test-tool
project: shell
priority: 1
estimated_minutes: 40
depends_on: ["S71-mcp-server-scaffold"]
modifies: ["mcp-server/src/tools/forge-test.ts", "mcp-server/src/server.ts"]
executor: glm
---

## 目标

实现 `forge_test` MCP 工具，能在指定目录运行 `forge test --json` 并返回结构化结果。

## 背景

Shell 的核心 pipeline 是 Test → Repair → Deploy。`forge_test` 是第一个也是最关键的工具。AI 调用这个工具后能拿到每个测试的 pass/fail 状态、gas 消耗、错误信息。

## 步骤

1. 创建 `mcp-server/src/tools/forge-test.ts`:
   ```typescript
   // 工具定义
   name: "forge_test"
   description: "Run Foundry tests on Solidity contracts. Returns structured JSON results."
   inputSchema: {
     project_dir: string,      // 项目目录 (包含 foundry.toml)
     test_filter?: string,     // 可选: 只跑匹配的测试 (--match-test)
     verbosity?: number,       // 0-5, 对应 -v to -vvvvv
     gas_report?: boolean      // 是否生成 gas report
   }
   ```
2. 实现逻辑:
   - 验证 `project_dir` 存在且包含 `foundry.toml`
   - 执行 `forge test --json` 子进程 (spawn, 不是 exec)
   - 设置超时: 120 秒
   - 解析 JSON 输出为结构化结果
   - 返回: `{ success: boolean, total: number, passed: number, failed: number, tests: ForgeTestResult[], gas_report?: object }`
3. 在 `server.ts` 注册此工具
4. 错误处理:
   - forge 未安装 → 返回 `{ error: "forge not found", install_hint: "curl -L https://foundry.paradigm.xyz | bash && foundryup" }`
   - 编译错误 → 返回编译错误详情
   - 超时 → 返回 timeout 错误

## 约束

- 子进程必须用 spawn (支持流式输出), 不用 exec
- 超时后必须 kill 子进程树
- 不要修改 forge 的输出格式，原样解析

## 验收标准

- [ ] 工具注册成功，MCP 客户端可发现
- [ ] 给定一个有 Foundry 项目的目录，返回结构化测试结果
- [ ] 测试失败时返回具体的失败信息 (assertion, revert reason)
- [ ] forge 不存在时返回友好错误提示
- [ ] 120秒超时正常工作

## 不要做

- 不要安装 Forge (Docker spec 负责)
- 不要修改 web-ui/ 的文件
