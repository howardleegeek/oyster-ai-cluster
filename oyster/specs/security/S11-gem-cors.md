---
task_id: GW-007
project: security
priority: P1
depends_on: []
modifies: ["gem-platform backend config"]
executor: glm
---

## 目标
将 GEM Backend CORS 从 ["*"] 改为白名单域名

## 步骤
1. 找到 GEM Backend 的 CORS 配置：
   `grep -r "CORS\|cors\|allow_origins" ~/Downloads/gem-platform/`
2. 修改为白名单：
   ```python
   CORS_ALLOW_ORIGINS = [
       "http://localhost:3000",
       "http://localhost:5173",
   ]
   ```
3. 重启 GEM Backend
4. 验证：
   ```bash
   curl -H "Origin: https://evil.com" -I http://localhost:8000/api/health
   ```
   响应不应包含 `Access-Control-Allow-Origin: *`

## 验收标准
- [ ] CORS 响应头仅返回白名单域名
- [ ] 来自 evil.com 的 Origin 被拒绝

## 回滚
恢复 `["*"]` 并重启

## 不要做
- 不修改 API 路由逻辑
- 不动前端代码
