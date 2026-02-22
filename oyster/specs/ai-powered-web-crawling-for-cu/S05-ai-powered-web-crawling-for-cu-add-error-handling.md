---
task_id: S05-ai-powered-web-crawling-for-cu-add-error-handling
project: ai-powered-web-crawling-for-cu
priority: 2
depends_on: ["S01-ai-powered-web-crawling-for-cu-bootstrap"]
modifies: ["backend/crawler.py", "backend/routes/web_crawler.py"]
executor: glm
---
## 目标
为爬取功能添加错误处理机制，确保在遇到异常时能够返回适当的错误信息

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
