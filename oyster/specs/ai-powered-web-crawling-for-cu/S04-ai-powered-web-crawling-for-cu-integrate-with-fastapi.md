---
task_id: S04-ai-powered-web-crawling-for-cu-integrate-with-fastapi
project: ai-powered-web-crawling-for-cu
priority: 1
depends_on: ["S01-ai-powered-web-crawling-for-cu-bootstrap"]
modifies: ["backend/main.py", "backend/routes/web_crawler.py"]
executor: glm
---
## 目标
将爬取功能集成到FastAPI的API端点中，支持通过API触发爬取任务

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
