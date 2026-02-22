---
task_id: S217-node-health
project: oyster-infra
priority: 2
depends_on: []
modifies: ["dispatch/node_health.py"]
executor: glm
---
## 目标
实现节点健康监控: 实时状态 + web 看板

## 约束
- 在 dispatch 目录内添加
- 写 pytest 测试
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_node_health.py 全绿
- [ ] 实时显示节点在线/离线
- [ ] SSH 连通性检测
- [ ] CPU/内存指标 (通过 SSH)

## 不要做
- 不留 TODO/FIXME/placeholder
