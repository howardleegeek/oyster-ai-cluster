---
task_id: S84-e2e-pipeline-test
project: shell
priority: 2
estimated_minutes: 40
depends_on: ["S72-forge-test-tool", "S73-forge-build-tool", "S74-read-report-tool", "S75-forge-deploy-tool", "S83-starter-templates"]
modifies: ["mcp-server/tests/e2e-pipeline.test.ts", "mcp-server/tests/setup.ts"]
executor: glm
---

## 目标

创建 E2E 测试验证完整的 Shell pipeline: Create → Build → Test → Report → Deploy。

## 步骤

1. 创建 `mcp-server/tests/setup.ts`:
   - 启动 MCP Server (stdio mode for testing)
   - 确认 Forge 和 Anvil 可用
   - 创建临时测试目录

2. 创建 `mcp-server/tests/e2e-pipeline.test.ts`:
   ```typescript
   // 测试场景 1: Happy Path
   test("full pipeline: create → build → test → deploy", async () => {
     // 1. 创建 ERC-20 项目
     const project = await callTool("create_project", {
       template: "erc20-basic",
       project_name: "test-token"
     });
     expect(project.build_success).toBe(true);

     // 2. 编译
     const build = await callTool("forge_build", {
       project_dir: project.project_dir
     });
     expect(build.success).toBe(true);
     expect(build.contracts.length).toBeGreaterThan(0);

     // 3. 跑测试
     const test = await callTool("forge_test", {
       project_dir: project.project_dir
     });
     expect(test.success).toBe(true);
     expect(test.passed).toBeGreaterThan(0);

     // 4. 读报告
     const report = await callTool("read_report", {
       project_dir: project.project_dir
     });
     expect(report.summary.failed).toBe(0);

     // 5. 部署
     const deploy = await callTool("forge_deploy", {
       project_dir: project.project_dir,
       contract_name: "Token",
       chain: "anvil"
     });
     expect(deploy.success).toBe(true);
     expect(deploy.address).toMatch(/^0x[a-fA-F0-9]{40}$/);
   });

   // 测试场景 2: Repair Loop
   test("repair loop: test fails → read report → repair", async () => {
     // 1. 创建有 bug 的合约
     // 2. 测试失败
     // 3. 读报告
     // 4. 调用 auto_repair
     // 5. 验证 patch 合理性
   });

   // 测试场景 3: Error Handling
   test("graceful errors: no forge, no project, no anvil", async () => {
     // 测试各种错误场景
   });
   ```

3. 添加到 package.json scripts: `"test:e2e": "tsx --test tests/e2e-pipeline.test.ts"`

## 约束

- 使用 Node.js 内置 test runner (node:test)
- 测试需要 Docker 环境 (Forge + Anvil)
- 每个测试清理临时目录
- 超时: 每个测试最多 60 秒

## 验收标准

- [ ] Happy path E2E 测试全过
- [ ] Repair loop 测试验证 patch 生成
- [ ] 错误场景测试返回友好消息
- [ ] 所有测试在 Docker 容器内可运行

## 不要做

- 不要依赖外部测试网 (只用 Anvil)
- 不要修改 web-ui/
