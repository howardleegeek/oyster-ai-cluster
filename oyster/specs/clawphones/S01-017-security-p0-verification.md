---
task_id: S01-017
project: clawphones
priority: 1
depends_on: []
modifies: ["proxy/tests/test_security_p0_fixes.py"]
executor: glm
---

## 目标
后端 API 安全测试：P0 修复验证

## 约束
- pytest
- 覆盖安全修复点

## 具体改动
- 完善 proxy/tests/test_security_p0_fixes.py
  - Admin key 常量时间比较验证
  - HTTPS-only 配置验证
  - 凭据环境变量读取验证
  - 签名密码环境变量验证

## 验收标准
- [ ] 安全修复测试全部通过
- [ ] 无敏感信息泄露
