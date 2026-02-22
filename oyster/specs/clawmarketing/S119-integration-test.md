---
task_id: S119-integration-test
project: clawmarketing
priority: 2
depends_on: ["S117-full-workflow"]
modifies: ["tests/test_integration.py"]
executor: glm
---
## 目标
编写端到端集成测试覆盖完整营销流程

## 约束
- 使用 pytest + httpx TestClient
- mock 外部 API (Twitter, Discord, LLM)
- 写 pytest 测试

## 验收标准
- [ ] pytest tests/test_integration.py 全绿
- [ ] 测试覆盖: 创建品牌 → 运行 campaign → 查看 analytics
- [ ] 所有外部调用使用 mock
- [ ] 测试覆盖率 > 80%

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
