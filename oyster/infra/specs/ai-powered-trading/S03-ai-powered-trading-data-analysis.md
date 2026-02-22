---
task_id: S03-ai-powered-trading-data-analysis
project: ai-powered-trading
priority: 2
depends_on: ["S01-ai-powered-trading-bootstrap"]
modifies: ["backend/data_analysis.py", "backend/utils.py"]
executor: glm
---
## 目标
开发数据分析模块，对获取的金融数据进行清洗和初步分析，如计算移动平均线

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
