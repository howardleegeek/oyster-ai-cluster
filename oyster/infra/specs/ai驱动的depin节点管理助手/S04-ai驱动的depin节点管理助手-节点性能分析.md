---
task_id: S04-ai驱动的depin节点管理助手-节点性能分析
project: ai驱动的depin节点管理助手
priority: 2
depends_on: ["S01-ai驱动的depin节点管理助手-bootstrap"]
modifies: ["backend/performance_analysis.py", "backend/ai_models/performance_model.py"]
executor: glm
---
## 目标
利用AI分析节点性能数据，识别潜在瓶颈和优化点

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
