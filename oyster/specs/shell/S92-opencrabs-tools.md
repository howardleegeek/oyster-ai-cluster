---
task_id: S92-opencrabs-tools
project: shell
priority: 3
estimated_minutes: 60
depends_on: ["S71-mcp-server-scaffold", "S72-forge-test-tool", "S73-forge-build-tool"]
modifies: ["INTEGRATION.md", "repo/opencrabs-tools/"]
executor: glm
---

## 目标

实现 Shell 与 OpenCrabs 的 Web3 工具集成，让 OpenCrabs 的 AI agent 能调用 shell-run 命令执行 Web3 开发任务。

## 步骤

1. **创建 `repo/opencrabs-tools/` 目录**:
   - `web3_detect.rs` — 检测项目类型 (EVM/Solana)，调用 `shell-run detect`
   - `web3_test.rs` — 运行测试，调用 `shell-run test --chain {chain}`
   - `web3_build.rs` — 构建项目，调用 `shell-run build --chain {chain}`
   - `web3_deploy.rs` — 部署到测试网，调用 `shell-run deploy --network {network}`
   - `web3_report.rs` — 读取 `reports/*.json` 返回结构化摘要
   - `mod.rs` — 注册所有工具到 OpenCrabs tool registry

2. **每个工具遵循 OpenCrabs Tool trait**:
   ```rust
   pub struct Web3Test;
   impl Tool for Web3Test {
       fn name(&self) -> &str { "web3_test" }
       fn description(&self) -> &str { "Run smart contract tests" }
       fn execute(&self, args: &Value) -> Result<Value> {
           // 1. Run shell-run test
           // 2. Parse report JSON
           // 3. Return structured result
       }
   }
   ```

3. **创建 brain 文件**:
   - `repo/opencrabs-tools/WEB3.md` — Web3 开发规则和约束
   - Agent 必须在 web3_test 后调用 web3_report 读取报告

4. **测试**:
   - `repo/opencrabs-tools/tests/integration.rs` — 集成测试

## 约束

- 遵循 OpenCrabs 现有 Tool trait 接口
- 所有工具通过 shell-run 间接调用 (不直接调用 forge/anchor)
- 报告驱动工作流必须强制执行

## 验收标准

- [ ] 6 个 Rust 工具文件编译通过
- [ ] `cargo test` 集成测试通过
- [ ] 工具注册到 OpenCrabs registry
- [ ] WEB3.md brain 文件包含报告驱动规则

## 不要做

- 不要修改 OpenCrabs 核心代码
- 不要直接调用 Foundry/Anchor CLI
- 不要添加新依赖到 OpenCrabs
