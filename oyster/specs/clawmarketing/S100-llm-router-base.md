---
task_id: S100-llm-router-base
project: clawmarketing
priority: 1
depends_on: []
modifies: ["backend/clients/llm_router.py", "backend/clients/providers/glm_client.py"]
executor: glm
---
## 目标
实现 LLM Router 基础架构和 GLM Provider

## 约束
- 使用已有的 FastAPI 框架
- 不新建超过 2 个文件
- 写 pytest 测试
- 基于 httpx 实现异步请求
- LLM Router 必须支持 provider 注册、优先级排序、自动 fallback
- GLM Provider 调用 api.z.ai 或 GLM 官方 API

## 验收标准
- [ ] pytest tests/test_llm_router.py::test_glm_provider 全绿
- [ ] GLM Provider 可正常调用 GLM API (mock 测试)
- [ ] LLM Router 可按优先级选择 Provider
- [ ] Router.chat(prompt) 返回 LLMResponse(content, model, latency_ms)

## 不要做
- 不动 frontend
- 不改 main.py 的路由结构
- 不留 TODO/FIXME/placeholder
