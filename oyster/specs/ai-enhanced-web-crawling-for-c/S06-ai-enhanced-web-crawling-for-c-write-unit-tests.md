---
task_id: S06-ai-enhanced-web-crawling-for-c-write-unit-tests
project: ai-enhanced-web-crawling-for-c
priority: 3
depends_on: ["S01-ai-enhanced-web-crawling-for-c-bootstrap"]
modifies: ["tests/test_web_crawler.py", "tests/test_api.py"]
executor: glm
---
## 目标
为网页爬取和解析功能编写单元测试

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
