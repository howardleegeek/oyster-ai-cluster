---
task_id: S05-ai-social-network-post-retrieval
project: ai-social-network
priority: 2
depends_on: ["S01-ai-social-network-bootstrap"]
modifies: ["backend/posts.py", "backend/main.py", "tests/test_posts.py"]
executor: glm
---
## 目标
实现用户获取帖子列表和单个帖子详情的功能

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
