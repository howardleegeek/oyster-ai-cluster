---
task_id: S106-brand-model
project: clawmarketing
priority: 1
depends_on: []
modifies: ["backend/models/models.py", "backend/database.py"]
executor: glm
---
## 目标
创建品牌配置数据库模型 (TELOS 系统)

## 约束
- 使用 SQLAlchemy ORM
- 不新建超过 2 个文件
- 写 pytest 测试

## 验收标准
- [ ] pytest tests/test_models.py::test_brand_config 全绿
- [ ] BrandConfig 模型包含: id, name, mission, goals, voice, strategy, twitter_token, created_at, updated_at
- [ ] 数据库表创建成功
- [ ] CRUD 操作测试通过

## 不要做
- 不动 frontend
- 不改 main.py 的路由结构
- 不留 TODO/FIXME/placeholder
