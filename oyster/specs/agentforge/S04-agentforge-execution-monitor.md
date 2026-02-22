---
task_id: S04-agentforge-execution-monitor
project: agentforge
priority: 2
depends_on: ["S03-agentforge-task-dispatch"]
modifies: ["api/routes/monitor.py", "services/monitor.py"]
executor: glm
---
## 目标
实现执行监控API，查询任务和工作流执行状态

## 技术方案
- 提供GET /tasks/{id}和GET /workflows/{id}/status端点
- 聚合任务执行指标
- 支持分页查询

## 约束
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] 可查询任务执行详情
- [ ] 可查询工作流整体状态
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
