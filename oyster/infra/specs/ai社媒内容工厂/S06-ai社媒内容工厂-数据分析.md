---
task_id: S06-ai社媒内容工厂-数据分析
project: ai社媒内容工厂
priority: 3
depends_on: ["S01-ai社媒内容工厂-bootstrap"]
modifies: ["backend/analytics.py", "backend/main.py", "tests/test_analytics.py"]
executor: glm
---
## 目标
开发数据分析和报告生成功能，跟踪内容表现和用户行为。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
