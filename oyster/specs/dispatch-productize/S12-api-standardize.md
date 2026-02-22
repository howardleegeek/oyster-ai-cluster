---
task_id: S12-api-standardize
project: dispatch-productize
priority: 1
estimated_minutes: 45
depends_on: ["S03-migrate-core-daemons"]
modifies: ["oyster/infra/dispatch/dispatch-controller.py"]
executor: glm
---

## 目标

标准化 Controller HTTP API，统一为 RESTful 风格，加错误处理和版本前缀。

## 当前 API

```
POST /v1/task_report   — Worker 上报任务结果
POST /v1/heartbeat     — Worker 心跳
GET  /v1/status        — Controller 概览
GET  /v1/workers       — Worker 列表
```

## 目标 API

```
# Health
GET  /health              — 健康检查（200/503）
GET  /metrics             — Prometheus 指标

# Tasks
GET  /api/v1/tasks                    — 列出任务（支持 ?status=pending&project=xxx）
GET  /api/v1/tasks/:id                — 获取单个任务详情
POST /api/v1/tasks                    — 创建任务（替代 dispatch.py start）
POST /api/v1/tasks/:id/claim          — Worker claim 任务
POST /api/v1/tasks/:id/heartbeat      — 任务心跳
POST /api/v1/tasks/:id/complete       — 任务完成
POST /api/v1/tasks/:id/fail           — 任务失败

# Workers
GET  /api/v1/workers                  — Worker 列表
POST /api/v1/workers/register         — Worker 自注册
POST /api/v1/workers/:id/heartbeat    — Worker 心跳

# Projects
GET  /api/v1/projects                 — 项目列表
GET  /api/v1/projects/:name/status    — 项目状态
POST /api/v1/projects/:name/dispatch  — 启动项目调度

# System
GET  /api/v1/status                   — 系统概览
GET  /api/v1/events                   — 事件日志（支持分页）
```

## 统一响应格式

```json
// 成功
{
  "ok": true,
  "data": { ... }
}

// 失败
{
  "ok": false,
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task S01-auth not found"
  }
}
```

## 向后兼容

- 保留旧 `/v1/*` 路由 6 个月，返回 301 重定向到 `/api/v1/*`
- Worker daemon 需要同步更新

## 约束

- RESTful 风格
- JSON request/response
- 统一错误码
- 分页支持（`?limit=50&offset=0`）

## 验收标准

- [ ] 所有新路由可用
- [ ] 旧路由返回 301 重定向
- [ ] 错误响应统一格式
- [ ] `GET /api/v1/tasks?status=pending` 返回分页结果
- [ ] OpenAPI/Swagger JSON 可选

## 不要做

- 不加认证（后续 spec）
- 不改 WebSocket（如有）
- 不删旧路由（只重定向）
