---
task_id: S07-depin-assistant-revenue-tracker
project: depin-assistant
priority: 1
depends_on: ["S06-depin-assistant-node-monitor"]
modifies: ["src/services/revenueTracker.js", "src/api/routes.js"]
executor: glm
---
## 目标
实现DePIN节点收益追踪API

## 技术方案
- 定义收益数据模型
- 提供GET /revenues端点
- 支持按节点和时间范围筛选

## 约束
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] 返回节点收益列表
- [ ] 支持时间范围过滤
- [ ] test 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
