---
task_id: S04-ai-driven-trustless-off-chain-fastapi-endpoints
project: ai-driven-trustless-off-chain
priority: 2
depends_on: ["S01-ai-driven-trustless-off-chain-bootstrap"]
modifies: ["backend/main.py", "backend/endpoints.py"]
executor: glm
---
## 目标
创建FastAPI端点以暴露验证后的数据

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
