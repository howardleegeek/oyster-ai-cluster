---
task_id: S219-pipeline-analytics
project: oyster-infra
priority: 2
depends_on: []
modifies: ["dispatch/pipeline_analytics.py"]
executor: glm
---
## 目标
实现 pipeline 性能分析: 完成率、平均时间、节点利用率

## 约束
- 在 dispatch 目录内添加
- 写 pytest 测试
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_pipeline_analytics.py 全绿
- [ ] 完成率统计
- [ ] 平均执行时间
- [ ] 节点利用率
- [ ] 导出 CSV/JSON

## 不要做
- 不留 TODO/FIXME/placeholder
