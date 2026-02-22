---
task_id: S06-新方向-ai驱动的nft估值平台-单元测试编写
project: 新方向-ai驱动的nft估值平台
priority: 3
depends_on: ["S01-新方向-ai驱动的nft估值平台-bootstrap"]
modifies: ["tests/test_data_collector.py", "tests/test_valuation.py", "tests/test_api.py"]
executor: glm
---
## 目标
为数据收集、估值算法和API接口编写单元测试，确保各模块功能正确。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
