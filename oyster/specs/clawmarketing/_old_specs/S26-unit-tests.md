---
task_id: S26-unit-tests
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
添加pytest单元测试，覆盖核心业务逻辑，目标覆盖率>70%

## 具体改动
1. 创建 backend/tests/test_auth.py - 认证测试
2. 创建 backend/tests/test_brands.py - 品牌CRUD测试
3. 创建 backend/tests/test_personas.py - Persona测试
4. 创建 backend/tests/test_agents.py - Agent测试
5. 添加 pytest.ini 配置
6. 运行 pytest 验证

## 验收标准
- [ ] pytest 可运行
- [ ] 覆盖率 > 70%
- [ ] 核心API有测试
