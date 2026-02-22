---
task_id: S05-ai-copilot-for-consumer-defi-w-analytics-integration
project: ai-copilot-for-consumer-defi-w
priority: 2
depends_on: ["S01-ai-copilot-for-consumer-defi-w-bootstrap"]
modifies: ["backend/analytics.py", "backend/main.py", "tests/test_analytics.py"]
executor: glm
---
## 目标
集成AI分析模块，提供用户消费行为和交易模式的分析

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
