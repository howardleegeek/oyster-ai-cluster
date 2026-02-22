---
task_id: S21-infra-backend-setup
project: clawphones
priority: 1
depends_on: []
modifies:
  - ~/Downloads/clawphones-backend/
executor: glm
---

## 目标
从 backend 模板创建 ClawPhones 后端基础设施，配置 Supabase PostgreSQL + Redis + Docker

## 约束
- 不动现有 proxy/server.py
- 使用 INFRA: backend 模板、Supabase、Redis
- 保持 API 兼容现有 iOS/Android 客户端

## 具体改动
1. 复制 backend 模板到 ~/Downloads/clawphones-backend
2. 配置 Supabase PostgreSQL 连接 (从 infra-configs/supabase.env)
3. 配置 Redis 连接
4. 创建数据库迁移脚本:
   - users 表
   - device_tokens 表
   - conversations 表
   - messages 表
   - usage_daily 表
   - push_tokens 表
   - analytics_events 表
   - crash_reports 表
   - vision_events 表 (新)
   - tasks 表 (新)
5. 创建 Docker 配置 (Dockerfile + docker-compose.yml)
6. 创建基础 API 路由结构

## 验收标准
- [ ] backend 项目结构完整
- [ ] Docker 可以 build
- [ ] 数据库迁移脚本可执行
- [ ] /health endpoint 返回正常

## 不要做
- 不修改现有 iOS/Android 代码
- 不删除现有 proxy/server.py

---

---
task_id: S22-migrate-auth-chat-api
project: clawphones
priority: 1
depends_on: ["S21-infra-backend-setup"]
modifies:
  - ~/Downloads/clawphones-backend/
executor: glm
---

## 目标
迁移现有 proxy/server.py 的 Auth + Chat API 到 clawphones-backend

## 约束
- 保持 API 兼容现有客户端
- 不改变现有接口签名
- 使用 JWT 替代简单 Bearer token

## 具体改动
1. 迁移 Auth API:
   - POST /v1/auth/register
   - POST /v1/auth/login
   - POST /v1/auth/apple
   - POST /v1/auth/refresh
   - GET /v1/user/profile
   - PUT /v1/user/profile
   - GET /v1/user/plan
   - GET /v1/user/ai-config
   - PUT /v1/user/ai-config

2. 迁移 Chat API:
   - POST /v1/chat/completions
   - POST /v1/conversations
   - GET /v1/conversations
   - GET /v1/conversations/{id}
   - POST /v1/conversations/{id}/chat
   - POST /v1/conversations/{id}/chat/stream (SSE)
   - DELETE /v1/conversations/{id}

3. LLM 路由保持现有逻辑:
   - free → DeepSeek
   - pro → Kimi
   - max → Claude

## 验收标准
- [ ] Auth API 测试通过
- [ ] Chat API 测试通过
- [ ] SSE streaming 正常工作
- [ ] Token tier 路由正确

## 不要做
- 不改 iOS/Android 客户端代码

---

---
task_id: S23-migrate-admin-files-api
project: clawphones
priority: 1
depends_on: ["S22-migrate-auth-chat-api"]
modifies:
  - ~/Downloads/clawphones-backend/
executor: glm
---

## 目标
迁移 Admin API + Files API 到 clawphones-backend

## 具体改动
1. Admin API:
   - POST /admin/tokens/generate
   - POST /admin/tokens/{token}/tier
   - POST /admin/push/announcement

2. Files API:
   - POST /v1/upload
   - POST /v1/conversations/{id}/upload
   - GET /v1/files/{file_id}

3. 其他 API:
   - POST /v1/analytics/events
   - POST /v1/crash-reports
   - GET /v1/crash-reports

## 验收标准
- [ ] Admin token 生成正常
- [ ] 文件上传/下载正常
- [ ] Analytics 和 Crash reports 存储正常

---

---
task_id: S24-frontend-admin-setup
project: clawphones
priority: 1
depends_on: ["S21-infra-backend-setup"]
modifies:
  - ~/Downloads/clawphones-admin/
executor: glm
---

## 目标
从 frontend 模板创建 ClawPhones Admin Portal

## 约束
- 使用 INFRA: frontend 模板、Supabase Auth、Vercel
- 复用现有 design system

## 具体改动
1. 复制 frontend 模板到 ~/Downloads/clawphones-admin
2. 配置 Supabase Auth
3. 创建页面:
   - Dashboard (用量统计)
   - Token 管理 (生成/禁用/查询)
   - 用户管理
   - 社区管理 (Sprint 13)
   - 任务管理 (Sprint 14-15)
4. 集成 backend API
5. 部署到 Vercel

## 验收标准
- [ ] 可以登录
- [ ] Token 管理页面可用
- [ ] 部署成功

## 不要做
- 不修改移动端代码

---

---
task_id: S25-mcp-integration
project: clawphones
priority: 2
depends_on: ["S22-migrate-auth-chat-api"]
modifies:
  - ~/Downloads/mcp-servers/
executor: glm
---

## 目标
将 ClawPhones 能力通过 MCP 协议暴露给外部应用

## 具体改动
1. 在 mcp-servers 中添加 clawphones-provider:
   - MCP tool: send_message (发送聊天消息)
   - MCP tool: create_conversation (创建对话)
   - MCP tool: get_conversations (获取对话列表)
   - MCP tool: upload_file (上传文件)
   - MCP resource: conversation://{id} (对话历史)

2. 文档:
   - MCP 工具说明
   - 集成示例

## 验收标准
- [ ] MCP server 可启动
- [ ] 工具可调用
- [ ] 文档完整

## 不要做
- 不修改现有移动端代码
