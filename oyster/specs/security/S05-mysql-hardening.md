---
task_id: GW-001
project: security
priority: P0
depends_on: []
modifies: ["docker-compose.yml"]
executor: glm
---

## 目标
收紧 MySQL 监听地址为 127.0.0.1 + 更换强密码

## 步骤
1. 找到包含 MySQL 服务的 docker-compose.yml（搜索 ~/Downloads/ 下所有 docker-compose 文件）
2. 备份：`cp docker-compose.yml docker-compose.yml.bak.$(date +%Y%m%d)`
3. 修改 ports 为 `"127.0.0.1:3306:3306"` 或移除端口映射
4. 生成强密码：`openssl rand -base64 24`
5. 替换 MYSQL_ROOT_PASSWORD 和 MYSQL_PASSWORD
6. 重启：`docker-compose up -d mysql`
7. 验证：`ss -tlnp | grep 3306` 应显示 127.0.0.1
8. 更新引用该数据库的应用配置中的密码

## 验收标准
- [ ] MySQL 仅监听 127.0.0.1:3306
- [ ] root 密码已更换为 24+ 字符强密码
- [ ] 应用正常连接

## 回滚
```bash
cp docker-compose.yml.bak.$(date +%Y%m%d) docker-compose.yml
docker-compose up -d mysql
```

## 不要做
- 不删除数据库数据
- 不修改表结构
