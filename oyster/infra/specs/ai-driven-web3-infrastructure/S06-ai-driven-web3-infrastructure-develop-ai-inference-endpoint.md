---
task_id: S06-ai-driven-web3-infrastructure-develop-ai-inference-endpoint
project: ai-driven-web3-infrastructure
priority: 3
depends_on: ["S01-ai-driven-web3-infrastructure-bootstrap"]
modifies: ["backend/ai_inference.py", "backend/main.py", "tests/test_ai_inference.py"]
executor: glm
---
## 目标
开发AI推理端点以处理智能合约数据

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
