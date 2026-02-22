---
task_id: S05-ai-driven-decentralized-financ-api-endpoints
project: ai-driven-decentralized-financ
priority: 2
depends_on: ["S01-ai-driven-decentralized-financ-bootstrap"]
modifies: ["backend/api/routes/advice.py", "backend/main.py"]
executor: glm
---
## 目标
创建API端点，允许前端应用查询AI生成的金融建议

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
