---
task_id: S218-auto-retry
project: oyster-infra
priority: 2
depends_on: []
modifies: ["dispatch/auto_retry.py"]
executor: glm
---
## 目标
实现自动重试失败任务 + 错误分析分类

## 约束
- 在 dispatch 目录内添加
- 写 pytest 测试
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_auto_retry.py 全绿
- [ ] 失败任务自动重试 (max 3 次)
- [ ] 错误分类: 可重试/不可重试
- [ ] 指数退避策略

## 不要做
- 不留 TODO/FIXME/placeholder
