## 目标

为 Shell MCP Server 创建 Docker 配置，预装 Foundry 工具链。

## 背景

MCP Server 需要在 Docker 容器内运行原生二进制 (forge, cast, anvil)，因为 WebContainer 无法运行它们。容器需要同时运行 MCP Server 和 Anvil 本地链。

## 步骤

1. 创建 `mcp-server/Dockerfile`:
   ```dockerfile
   FROM node:22-bookworm-slim AS base

   # 安装 Foundry
   RUN curl -L https://foundry.paradigm.xyz | bash
   ENV PATH="/root/.foundry/bin:${PATH}"
   RUN foundryup

   # 安装 MCP Server 依赖
   WORKDIR /app
   COPY package.json package-lock.json* ./
   RUN npm install --production
   COPY . .
   RUN npm run build

   EXPOSE 3001
   EXPOSE 8545

   # 启动脚本: 先启 Anvil，再启 MCP Server
   COPY entrypoint.sh /entrypoint.sh
   RUN chmod +x /entrypoint.sh
   CMD ["/entrypoint.sh"]
   ```
2. 创建 `mcp-server/entrypoint.sh`:
   - 后台启动 `anvil --host 0.0.0.0` (端口 8545)
   - 等待 Anvil 就绪 (curl health check, 最多 10 秒)
   - 前台启动 `node dist/server.js --transport sse --port 3001`
3. 创建 `mcp-server/docker-compose.yaml`:
   ```yaml
   services:
     mcp-server:
       build: .
       ports:
         - "3001:3001"   # MCP Server (SSE)
         - "8545:8545"   # Anvil RPC
       volumes:
         - ./projects:/app/projects  # 用户项目挂载
       environment:
         - NODE_ENV=production
         - ANVIL_BLOCK_TIME=1
   ```
4. 创建 `mcp-server/.dockerignore`: node_modules, dist, .git

## 约束

- 基于 node:22-bookworm-slim (与 web-ui Dockerfile 一致)
- Anvil 使用默认配置 (10 accounts, 10000 ETH each)
- 容器内存限制: 2GB
- 不要安装 Hardhat 或 Anchor (后续 spec 扩展)

## 验收标准

- [ ] `docker build -t shell-mcp .` 成功
- [ ] `docker run -p 3001:3001 -p 8545:8545 shell-mcp` 启动后 Anvil 和 MCP Server 都可用
- [ ] `forge --version` 在容器内返回版本号
- [ ] `curl http://localhost:8545 -d '{"method":"eth_blockNumber","params":[],"id":1,"jsonrpc":"2.0"}'` 返回区块号

## 不要做

- 不要修改 web-ui/ 的 Dockerfile
- 不要安装 Hardhat 或 Anchor