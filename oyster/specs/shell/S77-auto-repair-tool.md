---
task_id: S77-auto-repair-tool
project: shell
priority: 2
estimated_minutes: 35
depends_on: ["S71-mcp-server-scaffold", "S74-read-report-tool"]
modifies: ["mcp-server/src/tools/auto-repair.ts", "mcp-server/src/server.ts"]
executor: glm
---

## 目标

实现 `auto_repair` MCP 工具，根据测试报告分析失败原因并生成修复 patch。

## 背景

这是 Shell "Repair Loop" 的核心。AI 读报告 → 调用 auto_repair → 拿到 patch → apply → 再测试 → 循环直到全绿。

## 步骤

1. 创建 `mcp-server/src/tools/auto-repair.ts`:
   ```typescript
   name: "auto_repair"
   description: "Analyze test failures and generate a repair patch. Uses rule-based heuristics."
   inputSchema: {
     project_dir: string,
     report: object,           // read_report 的输出 (或 forge_test 的输出)
     source_files?: string[],  // 相关源文件路径 (自动检测如未提供)
     max_patches?: number      // 最多生成几个 patch (default: 3)
   }
   ```
2. 失败分析引擎 (规则匹配，不调 LLM):
   - `assertion` → 找到断言行，分析期望值 vs 实际值
   - `revert` → 提取 revert reason，定位 require/revert 语句
   - `overflow` → 建议添加 SafeMath 或 unchecked 块
   - `access_control` → 建议检查 msg.sender / onlyOwner
   - `gas` → 建议优化循环/存储
3. 读取相关源文件:
   - 从报告的 source_location 找到文件
   - 读取失败行 ± 20 行上下文
4. 返回:
   ```typescript
   {
     analysis: [{
       failure: string,
       root_cause: string,
       category: string,
       affected_file: string,
       affected_lines: [number, number],
       suggested_fix: string,  // 人类可读的修复建议
       patch: string           // unified diff 格式
     }],
     confidence: "high" | "medium" | "low",
     total_failures_analyzed: number
   }
   ```

## 约束

- 纯规则匹配 + 正则，不调用 LLM API
- patch 格式为 unified diff (可直接 `git apply`)
- 每个 patch 最多改 50 行
- 不要自动 apply patch (让 AI 决定)

## 验收标准

- [ ] 给定一个包含 assertion failure 的报告，生成合理的 patch
- [ ] 给定一个 revert 错误，正确定位 require 语句
- [ ] patch 是合法的 unified diff 格式
- [ ] confidence 评级合理

## 不要做

- 不要调用外部 LLM API
- 不要自动 apply patch 到源文件
- 不要修改 web-ui/
