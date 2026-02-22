---
task_id: S06-ai-powered-trading-testing
project: ai-powered-trading
priority: 3
depends_on: ["S01-ai-powered-trading-bootstrap"]
modifies: ["tests/test_data_ingestion.py", "tests/test_data_analysis.py", "tests/test_trading_strategy.py", "tests/test_api.py"]
executor: glm
---
## 目标
编写单元测试和集成测试，确保各模块功能正确性

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
