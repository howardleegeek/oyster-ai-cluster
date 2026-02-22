---
task_id: S04-ai-powered-trading-trading-strategy
project: ai-powered-trading
priority: 1
depends_on: ["S01-ai-powered-trading-bootstrap"]
modifies: ["backend/trading_strategy.py", "backend/signals.py"]
executor: glm
---
## 目标
实现基础交易策略模块，根据分析结果生成买卖信号

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
