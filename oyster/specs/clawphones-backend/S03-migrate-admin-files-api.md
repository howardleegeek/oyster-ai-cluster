---
task_id: S03-migrate-admin-files-api
project: clawphones-backend
priority: 1
depends_on: ["S02-migrate-auth-chat-api"]
modifies:
  - ~/Downloads/clawphones-backend/
executor: glm
---

## 目标
迁移 Admin API + Files API 到 clawphones-backend

## 具体改动
1. 创建 app/admin/ 模块:
   - app/admin/admin_router.py
   - app/admin/admin_service.py

2. Admin API:
   - POST /admin/tokens/generate - 生成设备 token
   - POST /admin/tokens/{token}/tier - 更新 token tier
   - POST /admin/tokens/{token}/disable - 禁用 token
   - POST /admin/push/announcement - 系统推送

3. 创建 app/files/ 模块:
   - app/files/files_router.py
   - app/files/files_service.py

4. Files API:
   - POST /v1/upload - 通用文件上传
   - POST /v1/conversations/{id}/upload - 会话文件上传
   - GET /v1/files/{file_id} - 获取文件
   - DELETE /v1/files/{file_id} - 删除文件

5. 创建 app/analytics/ 模块:
   - app/analytics/analytics_router.py
   - app/analytics/analytics_service.py

6. 其他 API:
   - POST /v1/analytics/events
   - POST /v1/crash-reports
   - GET /v1/crash-reports
   - PATCH /v1/crash-reports/{report_id}

7. 添加文件存储:
   - 配置本地存储路径 (uploads/, exports/)
   - 或集成 Supabase Storage

## 验收标准
- [ ] Admin token 生成正常
- [ ] 文件上传/下载正常
- [ ] Analytics 和 Crash reports 存储正常
- [ ] 测试通过

## 不要做
- 不改 iOS/Android 客户端代码
