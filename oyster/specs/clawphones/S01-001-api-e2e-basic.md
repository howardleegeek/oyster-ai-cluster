---
task_id: S01-001
project: clawphones
priority: 1
depends_on: []
modifies: ["proxy/test_api.py"]
executor: glm
---

## 目标
后端 API 端对端测试：健康检查、认证、CRUD 会话、聊天功能

## 约束
- 使用 Python pytest
- 覆盖核心 API 端点
- 可独立运行

## 具体改动
- 完善 proxy/test_api.py，添加：
  - `/health` 健康检查测试
  - `/v1/auth/register`, `/v1/auth/login`, `/v1/auth/refresh` 认证测试
  - `/v1/conversations` CRUD 测试
  - `/v1/conversations/{id}/chat` 聊天测试

## 验收标准
- [ ] pytest proxy/test_api.py 全绿
- [ ] 覆盖 20+ API 端点
