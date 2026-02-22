---
task_id: S74-read-report-tool
project: shell
priority: 1
estimated_minutes: 25
depends_on: ["S71-mcp-server-scaffold"]
modifies: ["mcp-server/src/tools/read-report.ts", "mcp-server/src/server.ts"]
executor: glm
---

## 目标

实现 `read_report` MCP 工具，读取最新的测试报告 (JSON) 并返回结构化分析。

## 背景

Shell 的 Report-Driven 工作流核心: AI 跑测试 → 读报告 → 分析失败原因 → 生成修复。这个工具是 AI 理解测试结果的关键接口。

## 步骤

1. 创建 `mcp-server/src/tools/read-report.ts`:
   ```typescript
   name: "read_report"
   description: "Read and analyze the latest test report. Returns structured failure analysis."
   inputSchema: {
     project_dir: string,       // 项目目录
     report_path?: string,      // 可选: 指定报告文件路径
     format?: "forge" | "hardhat" | "anchor"  // 报告格式 (default: auto-detect)
   }
   ```
2. 自动检测报告位置:
   - Forge: `project_dir/out/test-results.json` 或最新的 `forge test --json` 输出
   - Hardhat: `project_dir/test-results.json`
   - Anchor: `project_dir/.anchor/test-results.json`
3. 解析并返回:
   ```typescript
   {
     summary: { total, passed, failed, skipped },
     failures: [{
       test_name: string,
       contract: string,
       error_type: "assertion" | "revert" | "overflow" | "gas" | "other",
       error_message: string,
       source_location: { file, line },
       suggested_fix_category: "logic" | "access_control" | "arithmetic" | "state"
     }],
     gas_report?: { contract, function, avg_gas, median_gas }[],
     timestamp: string
   }
   ```
4. 如果没有报告文件，返回 `{ error: "no_report_found", hint: "Run forge_test first to generate a report" }`

## 约束

- 失败分类 (error_type) 基于 revert reason 关键词匹配
- suggested_fix_category 基于简单启发式规则
- 报告文件超过 10MB 时只返回 summary + 前 20 个 failures

## 验收标准

- [ ] 能读取 Forge JSON 测试报告
- [ ] 每个失败测试包含 error_type 分类
- [ ] 没有报告时返回友好提示
- [ ] 大报告有截断机制

## 不要做

- 不要调用 LLM 做分析 (纯规则匹配)
- 不要修改报告文件
- 不要修改 web-ui/
