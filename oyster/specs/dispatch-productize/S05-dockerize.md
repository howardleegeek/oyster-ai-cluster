---
task_id: S05-dockerize
project: dispatch-productize
priority: 1
estimated_minutes: 45
depends_on: ["S01-db-abstraction", "S04-health-endpoints"]
modifies: ["oyster/infra/dispatch/Dockerfile", "oyster/infra/dispatch/docker-compose.yml"]
executor: glm
---

## 目标

将 dispatch 系统容器化，客户 `docker-compose up -d` 一键启动。

## 实现

### Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# 入口点由 docker-compose 指定
CMD ["python3", "dispatch.py", "status"]
```

### docker-compose.yml

```yaml
version: "3.8"
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: dispatch
      POSTGRES_USER: dispatch
      POSTGRES_PASSWORD: ${DISPATCH_DB_PASSWORD:-dispatch_dev}
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dispatch"]
      interval: 5s
      timeout: 3s
      retries: 5

  guardian:
    build: .
    command: python3 guardian.py
    environment:
      DISPATCH_DB_BACKEND: postgres
      DISPATCH_DB_URL: postgresql://dispatch:${DISPATCH_DB_PASSWORD:-dispatch_dev}@postgres:5432/dispatch
    depends_on:
      postgres:
        condition: service_healthy
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8091/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    ports:
      - "8091:8091"

  reaper:
    build: .
    command: python3 pipeline/reaper_daemon.py
    environment:
      DISPATCH_DB_BACKEND: postgres
      DISPATCH_DB_URL: postgresql://dispatch:${DISPATCH_DB_PASSWORD:-dispatch_dev}@postgres:5432/dispatch
    depends_on:
      postgres:
        condition: service_healthy
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8092/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    ports:
      - "8092:8092"

  factory:
    build: .
    command: python3 pipeline/factory_daemon.py
    environment:
      DISPATCH_DB_BACKEND: postgres
      DISPATCH_DB_URL: postgresql://dispatch:${DISPATCH_DB_PASSWORD:-dispatch_dev}@postgres:5432/dispatch
    depends_on:
      postgres:
        condition: service_healthy
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8093/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    ports:
      - "8093:8093"

volumes:
  pgdata:
```

### requirements.txt

```
psycopg2-binary>=2.9
```

## 关键特性

1. **`restart: always`** — 容器挂了 Docker 自动重启（替代 launchd KeepAlive）
2. **healthcheck** — 结合 S04 的 `/health` endpoint，unhealthy 自动重启
3. **depends_on + condition** — 确保 PostgreSQL 就绪后才启动 daemon
4. **volumes** — PostgreSQL 数据持久化
5. **schema.sql 自动初始化** — 首次启动自动建表

## 约束

- 基于 python:3.11-slim（小镜像）
- 不打包 SSH 密钥到镜像（节点通信后续通过 API 替代）
- PostgreSQL 16（最新稳定版）
- 生产环境 `DISPATCH_DB_PASSWORD` 必须通过 `.env` 或 secrets 注入

## 验收标准

- [ ] `docker-compose build` 成功
- [ ] `docker-compose up -d` 启动 4 个服务（postgres + 3 daemon）
- [ ] `docker-compose ps` 全部 healthy
- [ ] daemon 被 kill 后 30s 内自动重启
- [ ] `docker-compose down && docker-compose up -d` 数据不丢失

## 不要做

- 不做 Kubernetes/Helm（后续 spec）
- 不处理 SSH 密钥挂载
- 不做 TLS/认证
