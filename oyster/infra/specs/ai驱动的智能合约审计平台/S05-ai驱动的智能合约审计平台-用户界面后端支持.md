---
task_id: S05-ai驱动的智能合约审计平台-用户界面后端支持
project: ai驱动的智能合约审计平台
priority: 2
depends_on: ["S01-ai驱动的智能合约审计平台-bootstrap"]
modifies: ["backend/main.py", "backend/endpoints/contracts.py"]
executor: glm
---
## 目标
为用户界面提供后端API支持，包括上传合约、查看审计进度和下载报告等功能。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
