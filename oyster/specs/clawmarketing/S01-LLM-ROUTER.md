---
task_id: S01-LLM-ROUTER
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - backend/agents/llm_router.py
executor: glm
---

## 目标
实现真正的 LLM Router，替换现有的 placeholder 代码，支持多 provider fallback

## 具体改动
1. 在 backend/agents/llm_router.py 中实现真实的 LLM 调用
2. 支持 provider 链: zai (glm-4-flash) → minimax → anthropic
3. 每个 provider 配置 URL、model、headers
4. 实现 generate() 方法，自动尝试每个 provider 直到成功
5. 添加 _build_request() 和 _parse_response() 辅助方法

## 验收标准
- [ ] python -c "import asyncio; from agents.llm_router import LLMRouter; asyncio.run(LLMRouter().generate('Say hi in 5 words'))" 能返回非空响应
- [ ] black backend/agents/llm_router.py 检查通过
- [ ] 如果没有配置任何 API key，返回清晰错误信息

## 不要做
- 不动其他文件
- 不改前端
