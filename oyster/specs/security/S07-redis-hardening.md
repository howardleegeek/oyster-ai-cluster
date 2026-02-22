---
task_id: GW-003
project: security
priority: P0
depends_on: []
modifies: ["docker-compose.yml"]
executor: glm
---

## 目标
为 Redis 添加 requirepass 认证 + bind 127.0.0.1，防止 RCE

## 步骤
1. 找到包含 Redis 服务的 docker-compose.yml
2. 备份配置
3. 生成强密码：`REDIS_PASS=$(openssl rand -base64 24)`
4. 修改 redis 服务：
   - command: `redis-server --requirepass ${REDIS_PASS} --bind 127.0.0.1 --protected-mode yes`
   - ports: `"127.0.0.1:6379:6379"` 或移除
5. 重启：`docker-compose up -d redis`
6. 验证：`redis-cli ping` 应返回 NOAUTH
7. 验证：`redis-cli -a ${REDIS_PASS} ping` 应返回 PONG
8. 更新所有引用 Redis 的应用配置

## 验收标准
- [ ] Redis 仅监听 127.0.0.1:6379
- [ ] 无密码 `redis-cli ping` 返回 NOAUTH
- [ ] protected-mode 已开启

## 回滚
```bash
cp docker-compose.yml.bak.$(date +%Y%m%d) docker-compose.yml
docker-compose up -d redis
```

## 不要做
- 不清空 Redis 数据
- 不禁用 Redis 持久化
