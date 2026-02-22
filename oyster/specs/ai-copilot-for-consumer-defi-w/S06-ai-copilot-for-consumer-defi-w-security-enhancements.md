---
task_id: S06-ai-copilot-for-consumer-defi-w-security-enhancements
project: ai-copilot-for-consumer-defi-w
priority: 2
depends_on: ["S01-ai-copilot-for-consumer-defi-w-bootstrap"]
modifies: ["backend/security.py", "backend/main.py", "tests/test_security.py"]
executor: glm
---
## 目标
实施安全增强措施，如输入验证、错误处理和防止常见漏洞

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
