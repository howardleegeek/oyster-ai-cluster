---
task_id: S113-memory-service
project: clawmarketing
priority: 2
depends_on: ["S112-memory-model"]
modifies: ["backend/services/memory_service.py"]
executor: glm
---
## 目标
实现记忆系统 CRUD 和过期清理逻辑

## 约束
- 封装记忆 CRUD 操作
- hot→warm→cold 自动降级
- 写 pytest 测试

## 验收标准
- [ ] pytest tests/test_memory_service.py 全绿
- [ ] save_memory(brand_id, content, metrics) 正常保存
- [ ] get_memories(brand_id, type) 正常查询
- [ ] cleanup_expired() 自动降级过期记忆

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
