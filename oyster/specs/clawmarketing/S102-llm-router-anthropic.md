---
task_id: S102-llm-router-anthropic
project: clawmarketing
priority: 1
depends_on: ["S101-llm-router-minimax"]
modifies: ["backend/clients/providers/anthropic_client.py"]
executor: glm
---
## 目标
实现 LLM Router 的 Anthropic Provider 作为最终 fallback

## 约束
- 复用 LLM Router 架构
- 不新建超过 1 个文件
- 写 pytest 测试
- 使用 anthropic Python SDK

## 验收标准
- [ ] pytest tests/test_llm_router.py::test_anthropic_provider 全绿
- [ ] Anthropic Provider 实现 BaseProvider 接口
- [ ] 完整 fallback 链: GLM → MiniMax → Anthropic 测试通过

## 不要做
- 不动 frontend
- 不改 main.py 的路由结构
- 不留 TODO/FIXME/placeholder
