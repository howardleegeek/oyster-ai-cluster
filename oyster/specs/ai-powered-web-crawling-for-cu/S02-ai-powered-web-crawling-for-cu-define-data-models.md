---
task_id: S02-ai-powered-web-crawling-for-cu-define-data-models
project: ai-powered-web-crawling-for-cu
priority: 1
depends_on: ["S01-ai-powered-web-crawling-for-cu-bootstrap"]
modifies: ["backend/models.py"]
executor: glm
---
## 目标
定义用于存储和表示爬取数据的Pydantic数据模型

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
