---
task_id: S10-docker-production
project: dispatch-productize
priority: 1
estimated_minutes: 45
depends_on: ["S01-db-abstraction", "S02-postgres-schema", "S09-integrate-health"]
modifies: ["oyster/infra/dispatch/Dockerfile", "oyster/infra/dispatch/docker-compose.yml", "oyster/infra/dispatch/docker-compose.prod.yml", "oyster/infra/dispatch/.env.example"]
executor: glm
---

## 目标

创建生产级 Docker Compose 配置，客户 `docker-compose up -d` 一键启动完整 dispatch 系统。

## 实现

### Dockerfile
```dockerfile
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl openssh-client rsync git && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:${HEALTH_PORT:-8090}/health || exit 1
```

### docker-compose.yml (开发)
- PostgreSQL 16
- Controller (port 8080)
- Guardian (port 8091)
- Reaper (port 8092)
- Factory (port 8093)
- 所有服务 `restart: always`
- PostgreSQL healthcheck gate

### docker-compose.prod.yml (生产覆盖)
- PostgreSQL 持久化 volume
- 日志 driver: json-file with rotation
- 资源限制 (memory/cpu)
- 网络隔离

### .env.example
```env
DISPATCH_DB_BACKEND=postgres
DISPATCH_DB_URL=postgresql://dispatch:changeme@postgres:5432/dispatch
DISPATCH_DB_PASSWORD=changeme
CONTROLLER_PORT=8080
```

### requirements.txt
```
aiohttp>=3.9
psycopg2-binary>=2.9
```

## 约束

- 基于 python:3.11-slim
- PostgreSQL 16-alpine
- 不打包 SSH 密钥到镜像
- 生产密码必须通过 .env 注入
- 镜像大小 < 500MB

## 验收标准

- [ ] `docker-compose build` 成功
- [ ] `docker-compose up -d` 启动 5 个服务
- [ ] `docker-compose ps` 全部 healthy（2 分钟内）
- [ ] `kill` 任意 daemon 容器后 30s 内自动重启
- [ ] `docker-compose down && docker-compose up -d` 数据不丢失
- [ ] `.env.example` 有注释说明每个变量

## 不要做

- 不做 Kubernetes/Helm
- 不做 TLS（后续 spec）
- 不做多节点 worker 容器（本 spec 只做控制面）
