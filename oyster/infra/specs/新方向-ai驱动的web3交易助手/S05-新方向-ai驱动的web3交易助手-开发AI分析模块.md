---
task_id: S05-新方向-ai驱动的web3交易助手-开发AI分析模块
project: 新方向-ai驱动的web3交易助手
priority: 2
depends_on: ["S01-新方向-ai驱动的web3交易助手-bootstrap"]
modifies: ["backend/ai_analysis.py", "backend/main.py"]
executor: glm
---
## 目标
开发AI分析模块，用于分析用户交易数据并提供智能交易建议。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
