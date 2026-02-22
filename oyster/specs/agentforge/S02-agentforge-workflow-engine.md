---
task_id: S02-agentforge-workflow-engine
project: agentforge
priority: 1
depends_on: ["S01-agentforge-agent-register"]
modifies: ["services/workflow_engine.py", "models/workflow.py"]
executor: glm
---
## 目标
实现工作流编排引擎，支持定义节点和边的DAG

## 技术方案
- 定义Workflow和Node模型
- 实现DAG拓扑排序验证
- 提供workflow创建和验证接口

## 约束
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] 可以创建包含多个节点的工作流
- [ ] 检测循环依赖并报错
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
