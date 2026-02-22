---
task_id: S02-ai驱动的智能合约审计平台-智能合约代码解析模块
project: ai驱动的智能合约审计平台
priority: 1
depends_on: ["S01-ai驱动的智能合约审计平台-bootstrap"]
modifies: ["backend/parser.py", "backend/models.py"]
executor: glm
---
## 目标
开发智能合约代码解析模块，支持解析Solidity代码并生成AST。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
