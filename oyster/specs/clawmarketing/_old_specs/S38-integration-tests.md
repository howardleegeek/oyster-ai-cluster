---
task_id: S38-integration-tests
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
添加集成测试

##具体改动
1. 创建 backend/tests/integration/test_auth_flow.py - 认证流程测试
2. 创建 backend/tests/integration/test_brands_flow.py - 品牌流程测试
3. 创建 backend/tests/integration/test_agents_flow.py - Agent流程测试
4. 使用TestClient测试完整API流程

##验收标准
- [ ] 认证流程可测试
- [ ] 品牌CRUD流程可测试
- [ ] Agent流程可测试
