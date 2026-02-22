---
task_id: S06-depin-assistant-node-monitor
project: depin-assistant
priority: 1
depends_on: []
modifies: ["src/services/nodeMonitor.js", "src/models/Node.js"]
executor: glm
---
## 目标
实现DePIN节点状态监控服务，定期检查节点在线状态

## 技术方案
- 使用Node.js定时任务检查节点
- 定义节点状态枚举和模型
- 存储检查结果到文件

## 约束
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] 定时检查节点并更新状态
- [ ] 记录节点在线/离线历史
- [ ] test 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
