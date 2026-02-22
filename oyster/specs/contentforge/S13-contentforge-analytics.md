---
task_id: S13-contentforge-analytics
project: contentforge
priority: 2
depends_on: ["S12-contentforge-publisher"]
modifies: ["services/analytics.py", "api/routes/analytics.py"]
executor: glm
---
## 目标
实现内容数据分析服务

## 技术方案
- 定义分析指标模型
- 统计曝光、互动等数据
- 提供可视化所需数据接口

## 约束
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] 返回内容表现统计
- [ ] 支持时间维度分析
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
