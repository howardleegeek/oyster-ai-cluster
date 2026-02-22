---
task_id: S02-ai-enhanced-web-crawling-for-c-implement-url-extractor
project: ai-enhanced-web-crawling-for-c
priority: 1
depends_on: ["S01-ai-enhanced-web-crawling-for-c-bootstrap"]
modifies: ["backend/web_crawler/url_extractor.py"]
executor: glm
---
## 目标
实现从网页内容中提取URL的功能

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
