---
task_id: S04-voice-ai-for-customer-service-response-generation
project: voice-ai-for-customer-service
priority: 2
depends_on: ["S01-voice-ai-for-customer-service-bootstrap"]
modifies: ["backend/response_generation.py"]
executor: glm
---
## 目标
开发基于客户意图生成自动回复的功能。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
