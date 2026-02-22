---
task_id: S01-012
project: clawphones
priority: 1
depends_on: []
modifies: ["proxy/server.py"]
executor: glm
---

## 目标
修复已知问题：SSE 流式响应

## 约束
- 后端 FastAPI
- 保持向后兼容

## 具体改动
- 修复 proxy/server.py
  - 实现 `/v1/conversations/{id}/chat/stream` SSE 端点
  - 确保流式响应正确工作

## 验收标准
- [ ] SSE 端点测试通过
- [ ] 现有非流式端点不受影响
