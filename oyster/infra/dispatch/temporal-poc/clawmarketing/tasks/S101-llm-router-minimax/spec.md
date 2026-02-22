## 目标
实现 LLM Router 的 MiniMax Provider

## 约束
- 复用 LLM Router 架构 (backend/clients/llm_router.py)
- 不新建超过 1 个文件
- 写 pytest 测试
- MiniMax API endpoint: api.minimax.io 或通过 anthropic 兼容接口

## 验收标准
- [ ] pytest tests/test_llm_router.py::test_minimax_provider 全绿
- [ ] MiniMax Provider 实现 BaseProvider 接口
- [ ] Router fallback 链: GLM → MiniMax 可正常切换

## 不要做
- 不动 frontend
- 不改 main.py 的路由结构
- 不留 TODO/FIXME/placeholder