---
task_id: AF06-oyster-agent-nodes
project: agentforge-v2
priority: 2
estimated_minutes: 45
depends_on: []
modifies: ["packages/components/nodes/"]
executor: glm
---
## 目标
添加 Oyster 自定义节点组件：Dispatch Task Node 和 Multi-Agent Node

## 技术方案
1. 在 `packages/components/nodes/` 添加 `oysterDispatch/` 节点：
   - OysterDispatchTask: 将子workflow包装为dispatch task
   - 参数: project, priority, estimated_minutes, node_preference
   - 输出: task_id, status, result
2. 添加 `oysterMultiAgent/` 节点：
   - OysterAgentPool: 并行分发多个任务到agent池
   - 参数: max_parallel, timeout, retry_count
   - 输出: aggregated_results

## 约束
- 遵循 Flowise 节点开发规范（INode interface）
- 每个节点一个目录，包含 .ts 定义和 icon
- 不改现有节点

## 验收标准
- [ ] OysterDispatchTask 节点出现在 workflow builder 节点列表中
- [ ] OysterAgentPool 节点出现在节点列表中
- [ ] 节点有正确的输入/输出参数定义
- [ ] npm run build 通过

## 不要做
- 不改现有节点
- 不改核心节点加载机制
