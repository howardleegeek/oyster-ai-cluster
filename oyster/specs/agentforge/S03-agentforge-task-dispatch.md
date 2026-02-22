---
task_id: S03-agentforge-task-dispatch
project: agentforge
priority: 2
depends_on: ["S02-agentforge-workflow-engine"]
modifies: ["services/task_dispatcher.py", "models/task.py"]
executor: glm
---
## 目标
实现任务分发服务，将任务分配给注册的Agent

## 技术方案
- 定义Task模型和状态枚举
- 实现轮询和随机分发策略
- 任务状态跟踪和更新

## 约束
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] 任务可以分发到指定agent
- [ ] 任务状态正确流转
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
