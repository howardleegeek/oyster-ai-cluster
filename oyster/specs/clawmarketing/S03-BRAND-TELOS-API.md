---
task_id: S03-BRAND-TELOS-API
project: clawmarketing
priority: 1
depends_on: [S02-BRAND-TELOS-MODEL]
modifies:
  - backend/routers/brands.py
executor: glm
---

## 目标
实现 Brand TELOS CRUD API endpoints

## 具体改动
1. 在 backend/routers/brands.py 中新增 PUT /{brand_id}/telos endpoint
2. 新增 GET /{brand_id}/telos endpoint
3. 验证用户权限 (get_current_user)

## 验收标准
- [ ] PUT /brands/1/telos 能存储 TELOS JSON
- [ ] GET /brands/1/telos 能读取
- [ ] black backend/routers/brands.py 检查通过

## 不要做
- 不动其他文件
