---
task_id: S107-brand-api
project: clawmarketing
priority: 1
depends_on: ["S106-brand-model"]
modifies: ["backend/api/brands.py", "backend/main.py"]
executor: glm
---
## 目标
实现品牌配置 CRUD API 端点

## 约束
- 使用 FastAPI 路由
- 不新建超过 1 个文件
- 写 pytest 测试

## 验收标准
- [ ] pytest tests/test_brands_api.py 全绿
- [ ] GET /api/v1/brands — 获取品牌列表
- [ ] POST /api/v1/brands — 创建品牌
- [ ] GET /api/v1/brands/{id} — 获取单个品牌
- [ ] PUT /api/v1/brands/{id} — 更新品牌
- [ ] DELETE /api/v1/brands/{id} — 删除品牌

## 不要做
- 不动 frontend
- 不改 main.py 除了 include_router
- 不留 TODO/FIXME/placeholder
