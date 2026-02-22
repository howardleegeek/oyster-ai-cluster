---
task_id: S05-self-improving-ai-agents-with-analytics-module
project: self-improving-ai-agents-with-
priority: 2
depends_on: ["S01-self-improving-ai-agents-with--bootstrap"]
modifies: ["backend/analytics.py", "backend/utils.py"]
executor: glm
---
## 目标
开发一个分析模块，用于评估和改进AI代理的性能。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
