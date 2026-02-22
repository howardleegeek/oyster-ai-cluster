---
task_id: GW-005
project: security
priority: P1
depends_on: []
modifies: ["docker-compose.yml"]
executor: glm
---

## 目标
启用 n8n 基本认证，关闭匿名访问

## 步骤
1. 找到 n8n 的 docker-compose.yml 配置
2. 备份配置
3. 取消注释或添加环境变量：
   ```yaml
   environment:
     - N8N_BASIC_AUTH_ACTIVE=true
     - N8N_BASIC_AUTH_USER=admin
     - N8N_BASIC_AUTH_PASSWORD=<openssl rand -base64 24>
   ```
4. 重启：`docker-compose up -d n8n`
5. 验证：`curl -s -o /dev/null -w "%{http_code}" http://localhost:5678` 应返回 401

## 验收标准
- [ ] 访问 n8n 需要登录
- [ ] 未认证访问返回 401
- [ ] 使用正确凭证可登录

## 回滚
注释掉 N8N_BASIC_AUTH 环境变量并重启

## 不要做
- 不删除 n8n 工作流数据
