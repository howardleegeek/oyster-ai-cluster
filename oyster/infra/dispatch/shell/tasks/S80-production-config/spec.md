## 目标

修复 Shell 的生产部署配置，从 Bolt 品牌完全迁移到 Shell。

## 步骤

1. 修改 `web-ui/wrangler.toml`:
   - `name = "shell"` (原来是 "bolt")

2. 修改 `web-ui/docker-compose.yaml`:
   - 所有 `bolt-ai` 改为 `shell`
   - image 名: `shell:production`, `shell:development`
   - 添加 MiniMax 环境变量:
     ```yaml
     - MINIMAX_API_KEY=${MINIMAX_API_KEY}
     - MINIMAX_API_BASE_URL=${MINIMAX_API_BASE_URL:-https://api.minimax.io/v1}
     ```
   - 添加 Shell MCP Server 环境变量:
     ```yaml
     - SHELL_MCP_URL=${SHELL_MCP_URL:-http://mcp-server:3001/sse}
     ```
   - 添加 mcp-server 服务:
     ```yaml
     mcp-server:
       build:
         context: ../mcp-server
         dockerfile: Dockerfile
       ports:
         - "3001:3001"
         - "8545:8545"
       volumes:
         - mcp-projects:/app/projects
     ```

3. 修改 `web-ui/Dockerfile`:
   - 将 target `bolt-ai-production` 改为 `shell-production`
   - 在 HEALTHCHECK 中添加 MCP Server 检查

4. 确保 `web-ui/package.json` 有 `dockerstart` 脚本:
   - 如果不存在: 添加 `"dockerstart": "npx wrangler pages dev ./build/client --port 5173 --ip 0.0.0.0 $(bash bindings.sh)"`

## 约束

- 不要删除现有的环境变量支持
- 保持向后兼容 (没有 MCP Server 也能跑)
- 不要改动 bindings.sh 的逻辑

## 验收标准

- [ ] wrangler.toml name 改为 "shell"
- [ ] docker-compose 中所有 "bolt" 引用替换为 "shell"
- [ ] MiniMax 和 MCP Server 环境变量已添加
- [ ] `dockerstart` 脚本存在且可执行
- [ ] `docker-compose --profile production config` 无错误

## 不要做

- 不要修改 mcp-server/ 的配置
- 不要删除现有 provider 环境变量