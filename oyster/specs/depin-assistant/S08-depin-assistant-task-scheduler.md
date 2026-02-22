---
task_id: S08-depin-assistant-task-scheduler
project: depin-assistant
priority: 2
depends_on: ["S06-depin-assistant-node-monitor"]
modifies: ["src/services/taskScheduler.js", "src/models/Task.js"]
executor: glm
---
## 目标
实现DePIN自动任务调度器

## 技术方案
- 定义任务模型和调度策略
- 实现基于节点状态的任务分配
- 支持定时任务和事件触发

## 约束
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] 可创建和管理定时任务
- [ ] 根据节点状态自动调度
- [ ] test 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
