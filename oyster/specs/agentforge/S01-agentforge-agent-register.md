---
task_id: S01-agentforge-agent-register
project: agentforge
priority: 1
depends_on: []
modifies: ["api/routes/agent.py", "models/agent.py", "schemas/agent.py"]
executor: glm
---
## 目标
实现Agent注册API，支持创建、查询、列表Agent基础信息

## 技术方案
- 使用FastAPI定义POST /agents和GET /agents端点
- 创建Agent模型和Pydantic Schema
- 内存存储实现简单的CRUD

## 约束
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] POST /agents 返回201和agent信息
- [ ] GET /agents 返回agent列表
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
