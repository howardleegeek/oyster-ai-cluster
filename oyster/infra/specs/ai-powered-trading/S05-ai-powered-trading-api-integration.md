---
task_id: S05-ai-powered-trading-api-integration
project: ai-powered-trading
priority: 2
depends_on: ["S01-ai-powered-trading-bootstrap"]
modifies: ["backend/main.py", "backend/routes/trading.py"]
executor: glm
---
## 目标
将交易信号通过FastAPI接口暴露，供前端或其他服务调用

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
