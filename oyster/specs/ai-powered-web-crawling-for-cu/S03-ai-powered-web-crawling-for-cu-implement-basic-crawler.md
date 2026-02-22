---
task_id: S03-ai-powered-web-crawling-for-cu-implement-basic-crawler
project: ai-powered-web-crawling-for-cu
priority: 1
depends_on: ["S01-ai-powered-web-crawling-for-cu-bootstrap"]
modifies: ["backend/crawler.py", "backend/routes/web_crawler.py"]
executor: glm
---
## 目标
实现基础的网页爬取功能，能够获取指定URL的内容

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
