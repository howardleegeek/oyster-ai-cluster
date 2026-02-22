---
task_id: S112-memory-model
project: clawmarketing
priority: 2
depends_on: ["S106-brand-model"]
modifies: ["backend/models/models.py", "backend/database.py"]
executor: glm
---
## 目标
创建三层记忆系统数据库模型

## 约束
- 使用 SQLAlchemy
- 三层: hot (7天), warm (30天), cold (归档)
- 写 pytest 测试

## 验收标准
- [ ] pytest tests/test_memory_model.py 全绿
- [ ] Memory 模型: id, brand_id, content, memory_type(hot/warm/cold), metrics_json, created_at, expires_at
- [ ] 支持按 brand_id 和 memory_type 查询

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
