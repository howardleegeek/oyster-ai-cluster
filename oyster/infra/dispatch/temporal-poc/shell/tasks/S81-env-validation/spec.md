## 目标

添加启动时环境变量验证，确保生产环境配置正确。

## 步骤

1. 创建 `web-ui/app/utils/env-check.ts`:
   ```typescript
   interface EnvStatus {
     provider: string;
     configured: boolean;
     key_prefix?: string;  // "sk-..." (只显示前3个字符)
   }

   export function checkEnvironment(): {
     llm_providers: EnvStatus[];
     mcp_server: { url: string; reachable: boolean };
     warnings: string[];
   }
   ```
   - 检查所有 LLM provider API key 是否已设置
   - 检查 SHELL_MCP_URL 是否设置
   - 返回配置状态摘要

2. 在 `web-ui/app/root.tsx` (或 layout) 的服务端 loader 中:
   - 调用 checkEnvironment()
   - 如果没有任何 LLM provider 配置，在控制台输出警告
   - 将配置状态传递给前端 (不包含 key 值!)

3. 在前端显示:
   - 如果没有 API key: 显示友好的设置引导
   - 如果 MCP Server 不可达: 显示 "Web3 tools offline" 提示

## 约束

- 绝对不要在前端暴露完整 API key
- 只显示 key 的前 3 个字符 + "***"
- 检查是异步的，不阻塞页面加载
- 警告只在开发模式显示在控制台

## 验收标准

- [ ] 启动时检测到 0 个 API key 时输出警告
- [ ] 前端可以看到哪些 provider 已配置
- [ ] API key 值不会泄露到前端
- [ ] 现有测试不受影响

## 不要做

- 不要阻塞应用启动
- 不要在前端显示完整 key
- 不要修改 mcp-server/