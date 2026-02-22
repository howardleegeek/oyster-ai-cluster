---
task_id: S34-unit-tests-coverage
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
添加pytest单元测试，目标覆盖率>70%

## 具体改动
1. 创建 backend/tests/test_brands.py - Brand CRUD测试
2. 创建 backend/tests/test_personas.py - Persona测试  
3. 创建 backend/tests/test_auth.py - 认证测试
4. 添加 pytest.ini 配置
5. 运行 pytest --cov 验证覆盖率

##验收标准
- [ ] 核心API有测试
- [ ] 覆盖率 > 70%
