---
task_id: G7-05-CP-CM
project: clawphones
priority: 1
depends_on: []
modifies: ["src/services/marketing_console.py", "src/api/dashboard.py"]
executor: glm
---
## 目标
移动端实时查看和操作营销活动

## 技术方案
1. 新增 `MarketingConsoleService`，暴露 CM 营销活动的 CRUD API
2. 实时数据聚合：活动状态、触达人数、转化率
3. 快速操作：暂停/启用活动、调整预算、查看实时数据
4. 集成 OI 推送事件到移动端

## 约束
- 复用现有 CM 数据模型
- 不修改移动端 UI 样式
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] 仪表盘加载 < 1s
- [ ] 支持活动启停操作
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
