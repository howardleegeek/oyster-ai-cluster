---
task_id: S04-ai社媒内容工厂-内容审核
project: ai社媒内容工厂
priority: 2
depends_on: ["S01-ai社媒内容工厂-bootstrap"]
modifies: ["backend/audit.py", "backend/main.py", "tests/test_audit.py"]
executor: glm
---
## 目标
集成内容审核功能，使用AI模型过滤不当内容并标记。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
