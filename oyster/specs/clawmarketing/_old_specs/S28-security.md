---
task_id: S28-security
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
安全加固 - Rate Limiting, Security Headers, 输入验证

##具体改动
1. 创建 backend/middleware/rate_limit.py - Rate limiting
2. 创建 backend/middleware/security.py - Security headers
3. 修改 main.py 注册中间件
4. 增强Pydantic验证

##验收标准
- [ ] Rate limiting生效 (测试: 快速请求被限流)
- [ ] Security headers设置正确
- [ ] 输入验证更严格
