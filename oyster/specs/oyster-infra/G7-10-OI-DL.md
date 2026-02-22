---
task_id: G7-10-OI-DL
project: oyster-infra
priority: 2
depends_on: ["G7-06-OI-ALL"]
modifies: ["src/data_lake/collector.py", "src/data_lake/queries.py"]
executor: glm
---
## 目标
建设跨项目数据湖，汇聚全链路营销数据

## 技术方案
1. 新增 `CrossProjectDataLake` 类，基于 ClickHouse
2. 收集事件：CM 活动数据, GP 交易数据, CV 分析数据, BP 发布数据
3. 预置分析查询：渠道ROI、用户旅程、转化漏斗
4. API 端点 `/api/v1/analytics/cross-project`

## 约束
- 事件驱动数据入湖
- 基础测试覆盖查询
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] 数据延迟 < 30s
- [ ] 支持 SQL 查询
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
