---
task_id: GW-002
project: security
priority: P0
depends_on: []
modifies: ["docker-compose.yml"]
executor: glm
---

## 目标
收紧 PostgreSQL 监听地址为 127.0.0.1 + 强制 scram-sha-256 认证

## 步骤
1. 找到包含 PostgreSQL 服务的 docker-compose.yml
2. 备份配置
3. 修改 ports 为 `"127.0.0.1:5433:5432"` 或移除端口映射
4. 生成强密码：`openssl rand -base64 24`
5. 替换 POSTGRES_PASSWORD
6. 重启：`docker-compose up -d postgres`
7. 验证：`ss -tlnp | grep 5433` 应显示 127.0.0.1
8. 更新引用该数据库的应用配置中的密码

## 验收标准
- [ ] PostgreSQL 仅监听 127.0.0.1:5433
- [ ] 密码已更换为强密码
- [ ] `psql` 连接需要密码

## 回滚
```bash
cp docker-compose.yml.bak.$(date +%Y%m%d) docker-compose.yml
docker-compose up -d postgres
```

## 不要做
- 不删除数据库数据
- 不修改 schema
