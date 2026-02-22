---
task_id: S03-ai驱动的智能合约审计平台-AI漏洞检测集成
project: ai驱动的智能合约审计平台
priority: 1
depends_on: ["S01-ai驱动的智能合约审计平台-bootstrap"]
modifies: ["backend/ai_integration.py", "backend/services.py"]
executor: glm
---
## 目标
集成AI模型用于检测智能合约中的漏洞和潜在风险。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
