---
task_id: S01-018
project: clawphones
priority: 1
depends_on: ["S01-001", "S01-002", "S01-008", "S01-010"]
modifies: ["proxy/tests/test_integration.py"]
executor: glm
---

## 目标
集成测试：端到端完整流程

## 约束
- 跨后端、iOS、Android
- 真实 API 调用

## 具体改动
- 创建 proxy/tests/test_integration.py
  - 完整用户注册→登录→创建会话→聊天→上传文件→导出数据流程
  - 验证多端数据一致性

## 验收标准
- [ ] 完整流程测试通过
- [ ] 数据一致性验证通过
