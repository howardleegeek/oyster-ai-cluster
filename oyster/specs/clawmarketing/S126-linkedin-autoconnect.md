---
task_id: S126-linkedin-autoconnect
project: clawmarketing
priority: 2
depends_on: ["S125-linkedin-client"]
modifies: ["backend/agents/linkedin_connect_agent.py", "backend/services/target_finder.py"]
executor: glm
---
## 目标
实现 Auto Connect 功能，按行业/职位筛选目标用户并发送连接请求

## 约束
- 基于 LinkedIn 搜索 API 查找目标用户
- 支持按 industry, title 过滤
- 尊重每周 100 个连接限制
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_auto_connect.py 全绿
- [ ] TargetFinder 支持按行业/职位搜索
- [ ] LinkedInConnectAgent 支持批量发送连接请求
- [ ] 已发送连接记录保存到数据库

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
