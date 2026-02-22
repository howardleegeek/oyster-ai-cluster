---
task_id: U02
title: "SHARED_CONTEXT 加请求/响应 JSON 示例"
depends_on: []
modifies: ["specs/clawmarketing/SHARED_CONTEXT.md"]
executor: glm
---

## 目标
SHARED_CONTEXT.md 的每个 API 接口必须有请求/响应 JSON 示例，不只是类型签名。

## 学到的
文章要求：API 列表含请求/响应示例。
我们的问题：SHARED_CONTEXT 只有类型签名和 Python 代码模式，GLM agent 对接时猜参数名/类型导致 PersonaEngine 构造函数错位。

## 改动
给每个 router 加 JSON 示例，比如：

```markdown
### POST /api/v1/auth/register
请求:
{
  "email": "user@example.com",
  "password": "securepass123",
  "full_name": "Howard Li",
  "organization_name": "Oyster Labs",
  "organization_slug": "oyster-labs"
}
响应 (201):
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "Howard Li",
  "organization_id": 1,
  "role": "owner"
}

### POST /api/v1/auth/login
请求:
{
  "email": "user@example.com",
  "password": "securepass123"
}
响应 (200):
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

所有 12 个 router 的主要端点都要加。

## 验收标准
- [ ] 12 个 router 每个至少 2 个端点有 JSON 示例
- [ ] 示例与实际 schema 一致（可运行验证）
