---
task_id: S01-013
project: clawphones
priority: 1
depends_on: ["S01-012"]
modifies: ["proxy/server.py"]
executor: glm
---

## 目标
修复已知问题：Token 禁用端点

## 约束
- 后端 FastAPI
- Admin 权限控制

## 具体改动
- 修复 proxy/server.py
  - 实现 `/admin/tokens/{token}/status` 端点
  - 支持 token 禁用/启用

## 验收标准
- [ ] Token 禁用测试通过
- [ ] Admin 权限验证通过
