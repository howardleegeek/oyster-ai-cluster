---
task_id: S01-005
project: clawphones
priority: 1
depends_on: []
modifies: ["proxy/tests/test_byzantine_malicious.py"]
executor: glm
---

## 目标
拜占庭容错测试：恶意行为防护

## 约束
- 测试异常输入、注入攻击
- 验证速率限制生效

## 具体改动
- 创建 proxy/tests/test_byzantine_malicious.py
  - SQL 注入测试
  - 恶意 prompt 注入测试
  - 速率限制绕过测试
  - 跨用户数据访问测试

## 验收标准
- [ ] 注入攻击被正确拦截
- [ ] 速率限制生效
- [ ] 跨用户隔离验证通过
