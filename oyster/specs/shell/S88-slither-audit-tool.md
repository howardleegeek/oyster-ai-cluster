---
task_id: S88-slither-audit-tool
project: shell
priority: 3
estimated_minutes: 30
depends_on: ["S71-mcp-server-scaffold", "S78-mcp-docker-foundry"]
modifies: ["mcp-server/src/tools/slither-audit.ts", "mcp-server/src/server.ts", "mcp-server/Dockerfile"]
executor: glm
---

## 目标

实现 `security_audit` MCP 工具，使用 Slither 静态分析检测合约安全漏洞。

## 步骤

1. 在 `mcp-server/Dockerfile` 添加 Slither:
   ```dockerfile
   RUN pip3 install slither-analyzer
   ```

2. 创建 `mcp-server/src/tools/slither-audit.ts`:
   ```typescript
   name: "security_audit"
   description: "Run Slither static analysis on Solidity contracts to detect vulnerabilities."
   inputSchema: {
     project_dir: string,
     severity_filter?: "high" | "medium" | "low" | "all"  // default: all
   }
   ```
3. 执行 `slither {project_dir} --json -`
4. 解析返回:
   ```typescript
   {
     total_issues: number,
     high: number,
     medium: number,
     low: number,
     informational: number,
     issues: [{
       severity: string,
       title: string,
       description: string,
       contract: string,
       function: string,
       lines: number[],
       recommendation: string,
       reference_url: string  // SWC registry link
     }],
     audit_time_seconds: number
   }
   ```

## 约束

- Slither 超时: 120 秒
- 只用 Slither (不装其他审计工具)
- severity_filter 可以过滤只看 high 级别

## 验收标准

- [ ] Slither 在 Docker 内可运行
- [ ] 包含 reentrancy 漏洞的合约能检测出
- [ ] 每个 issue 包含修复建议
- [ ] severity_filter 过滤正常工作

## 不要做

- 不要安装多个审计工具
- 不要修改 web-ui/
