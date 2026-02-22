---
task_id: S05-新方向-ai驱动的nft估值平台-API接口开发
project: 新方向-ai驱动的nft估值平台
priority: 2
depends_on: ["S01-新方向-ai驱动的nft估值平台-bootstrap"]
modifies: ["backend/main.py", "backend/api/endpoints.py"]
executor: glm
---
## 目标
开发用于前端交互的API接口，包括数据获取、估值请求和结果返回等。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
