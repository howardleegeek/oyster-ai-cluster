---
task_id: S06-ai-powered-web-crawling-for-cu-implement-unit-tests
project: ai-powered-web-crawling-for-cu
priority: 3
depends_on: ["S01-ai-powered-web-crawling-for-cu-bootstrap"]
modifies: ["tests/test_crawler.py", "tests/test_web_crawler_api.py"]
executor: glm
---
## 目标
为爬取功能编写单元测试，确保各个组件按预期工作

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
